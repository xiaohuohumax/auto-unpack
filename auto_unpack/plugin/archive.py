import logging
import shutil
import threading
from collections import defaultdict
from enum import Enum
from multiprocessing.pool import ThreadPool
from pathlib import Path
from typing import Any, List, Literal, Optional, Dict
from typing_extensions import Self
from uuid import uuid4

from pydantic import (BaseModel, Field, field_serializer, model_serializer,
                      model_validator)

from auto_unpack.plugin import HandlePluginConfig, Plugin
from auto_unpack.store import Context, FileData
from auto_unpack.util.file import (get_next_not_exist_path,
                                   is_path_in_includes, path_equal,
                                   read_file_lines, write_file)
from auto_unpack.util.sevenzip import ListResult, ResultCode, SevenZipUtil

logger = logging.getLogger(__name__)


class ArchiveInfoStatus(Enum):
    """
    文件信息枚举
    """
    # 未初始化
    INIT = (-1, 'Init')
    # 识别失败
    LIST_FAIL = (0, 'List Fail')
    # 识别为分卷
    LIST_VOLUME = (1, 'List Volume')
    # 识别成功
    LIST_SUCCESS = (2, 'List Success')
    # 测试失败
    TEST_FAIL = (3, 'Test Fail')
    # 测试成功
    TEST_SUCCESS = (4, 'Test Success')
    # 解压失败
    EXTRACT_FAIL = (5, 'Extract Fail')
    # 解压成功
    EXTRACT_SUCCESS = (6, 'Extract Success')


class ArchiveInfo(BaseModel):
    """
    压缩包信息
    """
    # 密码
    password: Optional[str] = None
    # 类型
    type: str
    # 是否分卷
    is_volume: bool
    # 分卷
    volumes: List[Path] = []
    # 入口文件路径
    main_path: Path = Field(exclude=True)

    @model_serializer(when_used='json')
    def serialize_v1(self) -> Dict[str, Any]:
        r = self.model_dump()
        if r['password'] is None:
            del r['password']
        if not r['is_volume']:
            del r['volumes']
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

    @field_serializer('status', when_used='json')
    def serialize_status(self, status: ArchiveInfoStatus) -> str:
        return status.value[1]


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

    # 详细信息
    groups: List[ArchiveStatGroup] = []


class ArchivePluginConfig(HandlePluginConfig):
    """
    压缩包处理插件配置
    """
    # 压缩包处理模式
    # list: 列出压缩包内文件信息，extract: 解压压缩包，test: 测试压缩包完整性
    mode: Literal['list', 'extract', 'test']
    # 密码文件路径
    password_path: Path = Path('passwords.txt')
    # 失败上下文 key
    fail_key: Optional[str] = None
    # 统计信息问件名
    stat_file_name: Optional[str] = None
    # 线程池最大线程数
    thread_max: int = 10

    # mode: extract 可用选项
    # 输出目录
    output_dir: Path = Path('output')
    # 是否保留压缩包目录
    keep_dir: bool = True

    @model_validator(mode='after')
    def validator(self) -> Self:
        password_path = self.password_path
        if not password_path.exists():
            raise ValueError(f"Password file `{password_path}` does not exist")
        return self


class ArchivePlugin(Plugin[ArchivePluginConfig]):
    """
    压缩包处理插件

    作用: 识别压缩包，测试压缩包完整性，解压压缩包
    """
    name: str = "archive"
    passwords: List[str] = []

    archive_files: List[ArchiveFile] = []

    cache_dir: Path = Path('.cache')
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
            if all(char == '-' for char in line) and len(line) > 0:
                start_index = i + 1
                break

        # 添加空密码到第一位
        passwords = [p for p in lines[start_index:] if len(p) > 0]
        self.passwords = [''] + passwords

        logger.info(
            f"Loaded {len(passwords)} passwords from `{self.config.password_path}`")

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
            include_successes = [c for c in success_archive_files
                                 if is_path_in_includes(archive_file.path, c.info.volumes)]
            if len(include_successes) > 0:
                # 已被识别的分卷
                success_archive_file = include_successes[0]
                archive_file.status = success_archive_file.status
                archive_file.info = success_archive_file.info
                archive_file.info_result = success_archive_file.info_result
                continue

            if self.config.mode == 'list':
                logger.info(f"Listing archive `{archive_file.path}`")

            for password in self.passwords:
                list_result = SevenZipUtil.list(archive_file.path, password)

                if list_result.code != ResultCode.NO_ERROR:
                    continue

                archive_file.status = ArchiveInfoStatus.LIST_SUCCESS
                archive_file.info_result = list_result
                archive_file.info = ArchiveInfo(
                    type=list_result.type,
                    is_volume=list_result.is_volume,
                    volumes=list_result.volume_paths,
                    password=password if password != '' else None,
                    main_path=list_result.volume_main_path,
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

            # 分卷压缩 且 主卷不是当前压缩包
            if len(archive_file.info.volumes) > 1 \
                    and not path_equal(archive_file.info.main_path, archive_file.path):
                archive_file.status = ArchiveInfoStatus.LIST_VOLUME

    def _test_archives_item(self, archive_file: ArchiveFile):
        """
        测试压缩包完整性

        :param archive_file: 待测试压缩包
        """
        info_result = archive_file.info_result
        if info_result is None:
            return

        logger.info(f"Testing archive `{archive_file.path}`")

        test_result = SevenZipUtil.test(
            info_result.file_path, info_result.password)

        if test_result.code == ResultCode.NO_ERROR:
            archive_file.status = ArchiveInfoStatus.TEST_SUCCESS
            return

        for password in self.passwords:
            test_result = SevenZipUtil.test(info_result.file_path, password)

            if test_result.code == ResultCode.NO_ERROR:
                archive_file.status = ArchiveInfoStatus.TEST_SUCCESS
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
        if self.config.mode != 'test':
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

        def extract_success():
            with self.file_lock:
                output = get_next_not_exist_path(
                    self.config.output_dir / archive_file.path.stem
                )
                shutil.move(output_cache_dir, output)
            logger.debug(
                f"Extracted archive `{output_cache_dir}` to `{output}`")
            archive_file.status = ArchiveInfoStatus.EXTRACT_SUCCESS
            archive_file.output = output

        extract_result = SevenZipUtil.extract(
            file_path=info_result.file_path,
            password=info_result.password,
            output_dir=output_cache_dir,
            overwrite='u',
            keep_dir=self.config.keep_dir,
        )
        if extract_result.code == ResultCode.NO_ERROR:
            extract_success()
            return

        for password in self.passwords:

            extract_result = SevenZipUtil.extract(
                file_path=info_result.file_path,
                password=password,
                output_dir=output_cache_dir,
                overwrite='u',
                keep_dir=self.config.keep_dir,
            )
            if extract_result.code == ResultCode.NO_ERROR:
                archive_file.info.password = password
                extract_success()
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
        if self.config.mode != 'extract':
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
            ArchiveInfoStatus.LIST_SUCCESS: [0, 'list_success'],
            ArchiveInfoStatus.LIST_VOLUME: [0, 'list_volume'],
            ArchiveInfoStatus.LIST_FAIL: [0, 'list_fail'],
            ArchiveInfoStatus.TEST_SUCCESS: [0, 'test_success'],
            ArchiveInfoStatus.TEST_FAIL: [0, 'test_fail'],
            ArchiveInfoStatus.EXTRACT_SUCCESS: [0, 'extract_success'],
            ArchiveInfoStatus.EXTRACT_FAIL: [0, 'extract_fail'],
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
        archive_status.groups = groups

        stat_json = archive_status.model_dump_json(
            indent=2,
            exclude_none=True,
        )

        stat_path = get_next_not_exist_path(
            self.global_config.info_dir / f'{self.config.stat_file_name}.json'
        )

        write_file(stat_path, stat_json)

        logger.info(f"Archive stat saved to `{stat_path}`")

    def _clear_cache(self):
        """
        清理缓存文件夹
        """
        for cache_dir in self.cache_dirs:
            shutil.rmtree(cache_dir, ignore_errors=True)

    def init(self):
        # 加载密码表
        self._load_passwords()

    def execute(self):
        try:
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
