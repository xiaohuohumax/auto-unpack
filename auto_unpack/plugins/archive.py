import logging
import shutil
import threading
from collections import defaultdict
from enum import Enum
from multiprocessing.pool import ThreadPool
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional
from uuid import uuid4

from pydantic import (
    BaseModel,
    Field,
    field_serializer,
    field_validator,
    model_serializer,
    model_validator,
)
from typing_extensions import Self

from auto_unpack.plugin import HandlePluginConfig, Plugin
from auto_unpack.store import Context, FileData
from auto_unpack.util.file import (
    get_next_not_exist_path,
    is_path_in_includes,
    path_equal,
    read_file_lines,
    write_file,
)
from auto_unpack.util.sevenzip import (
    ExtractResult,
    ListResult,
    Result,
    ResultCode,
    SevenZipUtil,
)
from auto_unpack.util.sevenzip.result import Attr

logger = logging.getLogger(__name__)


class ArchiveInfoStatus(Enum):
    """
    文件信息枚举
    """

    # 未初始化
    INIT = (-1, "Init")
    # 识别失败
    LIST_FAIL = (0, "List Fail")
    # 识别为分卷
    LIST_VOLUME = (1, "List Volume")
    # 识别成功
    LIST_SUCCESS = (2, "List Success")
    # 测试失败
    TEST_FAIL = (3, "Test Fail")
    # 测试成功
    TEST_SUCCESS = (4, "Test Success")
    # 解压失败
    EXTRACT_FAIL = (5, "Extract Fail")
    # 解压成功
    EXTRACT_SUCCESS = (6, "Extract Success")

    @property
    def tip(self):
        """
        状态码提示信息
        """
        return self.value[1]


class ArchiveInfo(BaseModel):
    """
    压缩包信息
    """

    # 是否分卷
    is_volume: bool
    # 密码
    password: Optional[str] = None
    # 压缩包属性
    attr: Attr
    # 分卷
    volumes: List[Path] = []
    # 入口文件路径
    main_path: Path = Field(exclude=True)

    @model_serializer(when_used="json")
    def serialize_v1(self) -> Dict[str, Any]:
        r = self.model_dump(exclude_none=True)
        if not r["is_volume"]:
            del r["volumes"]

        if "path" in r["attr"]:
            del r["attr"]["path"]
        return r


class ArchiveError(BaseModel):
    """
    异常信息
    """

    # 命令行输出
    message: str
    # 命令行错误代码
    code: Optional[ResultCode] = None


class ArchiveFile(BaseModel):
    """
    压缩包文件
    """

    # 状态
    status: ArchiveInfoStatus = Field(exclude=True)
    # 路径
    path: Path
    # 输出路径
    output: Optional[Path] = None
    # 识别信息
    info: Optional[ArchiveInfo] = None
    # 异常信息
    error: Optional[ArchiveError] = None

    # 上下文数据(暂存)
    file_data: FileData = Field(exclude=True)
    # 识别结果(暂存)
    info_result: Optional[ListResult] = Field(None, exclude=True)


class ArchiveStatGroup(BaseModel):
    """
    压缩包统计信息分组
    """

    # 状态
    status: ArchiveInfoStatus
    # 统计信息
    archives: List[ArchiveFile] = []

    @field_serializer("status", when_used="json")
    def serialize_status(self, status: ArchiveInfoStatus) -> str:
        return status.tip


# 结果处理模式
Result_Processing_Mode = Literal["strict", "greedy"]


class ArchiveStat(BaseModel):
    """
    压缩包统计信息
    """

    # 文件数
    count: int = 0

    # 各种状态数量
    list_success: Optional[int] = None
    list_volume: Optional[int] = None
    list_fail: Optional[int] = None
    test_success: Optional[int] = None
    test_fail: Optional[int] = None
    extract_success: Optional[int] = None
    extract_fail: Optional[int] = None
    # 结果处理模式
    result_processing_mode: Result_Processing_Mode = "strict"

    # 详细信息
    groups: List[ArchiveStatGroup] = []


class ArchivePluginConfig(HandlePluginConfig):
    """
    压缩包处理插件配置
    """

    name: Literal["archive"] = Field(default="archive", description="压缩包处理插件")
    # 压缩包处理模式
    mode: Literal["list", "extract", "test"] = Field(
        description="压缩包处理模式\nlist: 列出压缩包内文件信息\nextract: 解压压缩包\ntest: 测试压缩包完整性"
    )
    password_path: Path = Field(
        default_factory=lambda: Path("passwords.txt"),
        description="密码表文件路径(默认: passwords.txt)",
    )
    fail_key: Optional[str] = Field(
        default=None, description="失败上下文 key(默认: null)"
    )
    stat_file_name: Optional[str] = Field(
        default=None, description="统计信息文件名，不同模式对应不同统计信息(默认: null)"
    )
    thread_max: int = Field(
        default=10,
        description="线程池最大线程数(默认: 10)",
        json_schema_extra={"minimum": 1},
    )
    result_processing_mode: Result_Processing_Mode = Field(
        default="strict",
        description="结果处理模式(默认: strict)\nstrict: 严格模式[结果绝对依靠 7-zip 命令行输出]\ngreedy: 贪婪模式[7-zip 返回某些错误码时, 也会尝试识别/测试/解压]",
    )
    # mode: extract 可用选项
    output_dir: Path = Field(
        default_factory=lambda: Path("output"),
        description="压缩包存放目录(默认: output)",
    )
    keep_dir: bool = Field(
        default=True, description="是否保持解压后的文件夹结构(默认: true)"
    )

    @model_validator(mode="after")
    def validator(self) -> Self:
        password_path = self.password_path
        if not password_path.exists():
            raise ValueError(f"Password file `{password_path}` does not exist")
        return self

    @field_validator("thread_max")
    @classmethod
    def validate_thread_max(cls, v: int):
        if v <= 0:
            raise ValueError(f"Thread max should be greater than 0, but got `{v}`")
        return v


Result_Level = Literal["success", "warning", "error"]


class ArchivePlugin(Plugin[ArchivePluginConfig]):
    """
    压缩包处理插件

    作用: 识别压缩包，测试压缩包完整性，解压压缩包
    """

    name: str = "archive"
    passwords: List[str] = []

    archive_files: List[ArchiveFile] = []

    cache_dir: Path = Path(".cache")
    cache_dirs: List[Path] = []
    file_lock = threading.Lock()

    def _load_passwords(self):
        """
        加载密码表
        """
        self.passwords = []
        lines = read_file_lines(self.config.password_path)

        # 计算密码表起始位置
        start_index = 0
        for i, line in enumerate(lines):
            if all(char == "-" for char in line) and len(line) > 0:
                start_index = i + 1
                break

        # 添加空密码到第一位
        passwords = [p for p in lines[start_index:] if len(p) > 0]
        self.passwords = [""] + passwords

        logger.info(
            f"Loaded {len(passwords)} passwords from `{self.config.password_path}`"
        )

    def _get_result_level(self, result: Result) -> Result_Level:
        """
        获取返回结果的级别

        ```
        success: 成功（无错误）
        warning: 警告（存在错误，但不影响操作）
        error: 错误（存在错误，影响操作）
        ```

        :param result: 结果
        :return: 级别
        """
        if self.config.result_processing_mode == "greedy":
            # 贪婪模式

            # 关于 p7zip 解压缩较大的RAR格式文件 BUG ISSUE #2
            # 触发条件：
            # Type = Rar
            # Code = HEADERS_ERROR => Headers Error in encrypted archive.
            # Characteristics = Recovery
            if (
                result.code == ResultCode.HEADERS_ERROR
                and result.attr.type == "Rar"
                and "Recovery" in result.attr.characteristics
            ):
                return "warning"

        return "success" if result.code == ResultCode.NO_ERROR else "error"

    def _list_archives_item(self, archive_files: List[ArchiveFile]):
        """
        识别压缩包

        :param archive_files: 待识别压缩包列表
        """
        # 识别成功的压缩包
        success_archive_files: List[ArchiveFile] = []

        for archive_file in archive_files:
            # 跳过文件夹
            if archive_file.path.is_dir():
                error_message = f"Skipping directory `{archive_file.path}`"
                logger.warning(error_message)

                archive_file.status = ArchiveInfoStatus.LIST_FAIL
                archive_file.error = ArchiveError(message=error_message)
                continue

            # 跳过已被识别的分卷
            is_included = any(
                (
                    c
                    for c in success_archive_files
                    if is_path_in_includes(archive_file.path, c.info.volumes)
                )
            )
            if is_included:
                continue

            if self.config.mode == "list":
                logger.info(f"Listing archive `{archive_file.path}`")

            for password in self.passwords:
                list_result = SevenZipUtil.list(archive_file.path, password)

                level = self._get_result_level(list_result)
                if level == "error":
                    continue

                archive_file.status = ArchiveInfoStatus.LIST_SUCCESS
                archive_file.info_result = list_result
                archive_file.info = ArchiveInfo(
                    attr=list_result.attr,
                    is_volume=list_result.is_volume,
                    volumes=list_result.volume_paths,
                    password=password if password != "" else None,
                    main_path=list_result.volume_main_path,
                )
                if level == "warning":
                    archive_file.error = ArchiveError(
                        message=list_result.message,
                        code=list_result.code,
                    )
                success_archive_files.append(archive_file)
                break
            else:
                archive_file.status = ArchiveInfoStatus.LIST_FAIL
                archive_file.error = ArchiveError(
                    message=list_result.message,
                    code=list_result.code,
                )

    def _list_archives(self):
        """
        识别压缩包
        """
        self.archive_files = []
        context = self.load_context()

        # 线程分组 相同文件夹下的文件归为一组
        group = defaultdict(list)

        # 上下文转化为压缩包文件 ArchiveFile
        for file_data in context.file_datas:
            archive_file = ArchiveFile(
                status=ArchiveInfoStatus.INIT,
                path=file_data.path,
                file_data=file_data,
            )
            self.archive_files.append(archive_file)
            parent = file_data.path.parent
            group[str(parent.resolve())].append(archive_file)

        # 多线程识别
        pool = ThreadPool(self.config.thread_max)

        for _, archive_files in group.items():
            pool.apply_async(self._list_archives_item, args=(archive_files,))

        pool.close()
        pool.join()

        # 标记分卷子卷
        for archive_file in self.archive_files:
            if archive_file.status != ArchiveInfoStatus.LIST_SUCCESS:
                continue

            # 不是分卷
            if (
                not path_equal(archive_file.info.main_path, archive_file.path)
                or len(archive_file.info.volumes) < 2
            ):
                continue

            for archive_file_item in self.archive_files:
                if archive_file_item == archive_file:
                    continue
                if not is_path_in_includes(
                    archive_file_item.path, archive_file.info.volumes
                ):
                    continue

                archive_file_item.status = ArchiveInfoStatus.LIST_VOLUME
                # 拷贝参数
                archive_file_item.info = archive_file.info.model_copy()
                archive_file_item.info_result = archive_file.info_result.model_copy()
                archive_file_item.error = None

    def _test_archives_item(self, archive_file: ArchiveFile):
        """
        测试压缩包完整性

        :param archive_file: 待测试压缩包
        """
        info_result = archive_file.info_result
        if info_result is None:
            return

        logger.info(f"Testing archive `{archive_file.path}`")

        test_result = SevenZipUtil.test(info_result.file_path, info_result.password)
        level = self._get_result_level(test_result)

        if level in ["success", "warning"]:
            archive_file.status = ArchiveInfoStatus.TEST_SUCCESS
            if level == "warning":
                archive_file.error = ArchiveError(
                    message=test_result.message,
                    code=test_result.code,
                )
            return

        for password in self.passwords:
            test_result = SevenZipUtil.test(info_result.file_path, password)
            level = self._get_result_level(test_result)

            if level in ["success", "warning"]:
                archive_file.status = ArchiveInfoStatus.TEST_SUCCESS
                if level == "warning":
                    archive_file.error = ArchiveError(
                        message=test_result.message,
                        code=test_result.code,
                    )
                # 更新密码
                archive_file.info.password = password
                break
        else:
            archive_file.status = ArchiveInfoStatus.TEST_FAIL
            archive_file.error = ArchiveError(
                message=test_result.message,
                code=test_result.code,
            )

    def _test_archives(self):
        """
        测试压缩包完整性
        """
        if self.config.mode != "test":
            return

        pool = ThreadPool(self.config.thread_max)

        for archive_file in self.archive_files:
            if archive_file.status != ArchiveInfoStatus.LIST_SUCCESS:
                continue
            pool.apply_async(self._test_archives_item, args=(archive_file,))

        pool.close()
        pool.join()

    def _create_new_cache_dir(self) -> Path:
        """
        创建新的缓存目录

        :return: 缓存目录路径
        """
        new_cache_dir = self.cache_dir / str(uuid4())
        while new_cache_dir.exists():
            new_cache_dir = self.cache_dir / str(uuid4())
        new_cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dirs.append(new_cache_dir)
        return new_cache_dir

    def _extract_archives_item(self, archive_file: ArchiveFile):
        """
        解压压缩包

        :param archive_file: 待解压压缩包
        """
        info_result = archive_file.info_result
        if info_result is None:
            return

        logger.info(f"Extracting archive `{archive_file.path}`")

        output_cache_dir = self._create_new_cache_dir()

        def extract_success(result: ExtractResult, level: Result_Level):
            with self.file_lock:
                output = get_next_not_exist_path(
                    self.config.output_dir / archive_file.path.stem
                )
                shutil.move(output_cache_dir, output)
            logger.debug(f"Extracted archive `{output_cache_dir}` to `{output}`")
            archive_file.status = ArchiveInfoStatus.EXTRACT_SUCCESS

            if level == "warning":
                archive_file.error = ArchiveError(
                    message=result.message,
                    code=result.code,
                )
            archive_file.output = output

        extract_result = SevenZipUtil.extract(
            file_path=info_result.file_path,
            password=info_result.password,
            output_dir=output_cache_dir,
            overwrite="u",
            keep_dir=self.config.keep_dir,
        )
        level = self._get_result_level(extract_result)

        if level in ["success", "warning"]:
            extract_success(extract_result, level)
            return

        for password in self.passwords:
            extract_result = SevenZipUtil.extract(
                file_path=info_result.file_path,
                password=password,
                output_dir=output_cache_dir,
                overwrite="u",
                keep_dir=self.config.keep_dir,
            )

            level = self._get_result_level(extract_result)

            if level in ["success", "warning"]:
                archive_file.info.password = password
                extract_success(extract_result, level)
                break

            # 解压失败，生成新的缓存目录
            output_cache_dir = self._create_new_cache_dir()
        else:
            archive_file.status = ArchiveInfoStatus.EXTRACT_FAIL
            archive_file.error = ArchiveError(
                message=extract_result.message,
                code=extract_result.code,
            )

    def _extract_archives(self):
        """
        解压压缩包
        """
        if self.config.mode != "extract":
            return

        if not self.config.output_dir.exists():
            self.config.output_dir.mkdir(parents=True, exist_ok=True)

        pool = ThreadPool(self.config.thread_max)

        for archive_file in self.archive_files:
            if archive_file.status != ArchiveInfoStatus.LIST_SUCCESS:
                continue
            pool.apply_async(self._extract_archives_item, args=(archive_file,))

        pool.close()
        pool.join()

    def _save_context(self):
        """
        保存上下文
        """
        success_status = [
            ArchiveInfoStatus.LIST_VOLUME,
            ArchiveInfoStatus.LIST_SUCCESS,
            ArchiveInfoStatus.TEST_SUCCESS,
            ArchiveInfoStatus.EXTRACT_SUCCESS,
        ]

        fail_status = [
            ArchiveInfoStatus.INIT,
            ArchiveInfoStatus.LIST_FAIL,
            ArchiveInfoStatus.TEST_FAIL,
            ArchiveInfoStatus.EXTRACT_FAIL,
        ]

        # 上下文数据
        success_file_datas: List[FileData] = []
        fail_file_datas: List[FileData] = []

        for archive_file in self.archive_files:
            if archive_file.status in success_status:
                success_file_datas.append(archive_file.file_data)
            elif archive_file.status in fail_status:
                fail_file_datas.append(archive_file.file_data)

        self.save_context(Context(file_datas=success_file_datas))

        if self.config.fail_key is not None:
            context = Context(file_datas=fail_file_datas)
            self.save_context(context, self.config.fail_key)

    def _print_archive_stat(self):
        """
        打印统计信息
        """
        if self.config.stat_file_name is None:
            return

        # 各阶段数量统计
        count_map = {
            ArchiveInfoStatus.LIST_SUCCESS: [0, "list_success"],
            ArchiveInfoStatus.LIST_VOLUME: [0, "list_volume"],
            ArchiveInfoStatus.LIST_FAIL: [0, "list_fail"],
            ArchiveInfoStatus.TEST_SUCCESS: [0, "test_success"],
            ArchiveInfoStatus.TEST_FAIL: [0, "test_fail"],
            ArchiveInfoStatus.EXTRACT_SUCCESS: [0, "extract_success"],
            ArchiveInfoStatus.EXTRACT_FAIL: [0, "extract_fail"],
        }

        archive_status = ArchiveStat(groups=[])
        groups_map = defaultdict(list)

        for archive_file in self.archive_files:
            groups_map[archive_file.status].append(archive_file)
            item = count_map.get(archive_file.status, None)
            if item is not None:
                item[0] += 1

        for _, item in count_map.items():
            if item[0] > 0:
                setattr(archive_status, item[1], item[0])

        groups = [
            ArchiveStatGroup(
                status=status,
                archives=archive_files,
            )
            for status, archive_files in groups_map.items()
        ]

        archive_status.count = len(self.archive_files)
        archive_status.result_processing_mode = self.config.result_processing_mode
        archive_status.groups = groups

        stat_json = archive_status.model_dump_json(
            indent=2,
            exclude_none=True,
        )

        stat_path = get_next_not_exist_path(
            self.global_config.info_dir / f"{self.config.stat_file_name}.json"
        )

        write_file(stat_path, stat_json)

        logger.info(f"Archive stat saved to `{stat_path}`")

    def _clear_cache(self):
        """
        清理缓存文件夹
        """
        for cache_dir in self.cache_dirs:
            shutil.rmtree(cache_dir, ignore_errors=True)

    def execute(self):
        try:
            # 加载密码表
            self._load_passwords()
            # 解析压缩包
            self._list_archives()
            # 测试压缩包
            self._test_archives()
            # 解压压缩包
            self._extract_archives()
            # 保存上下文
            self._save_context()
            # 打印统计信息
            self._print_archive_stat()
        finally:
            # 清理缓存文件夹
            self._clear_cache()
