import os
import re
from enum import Enum
from pathlib import Path
from typing import Callable, List, Literal, Optional, Tuple

from pydantic import BaseModel, ConfigDict, computed_field


class ResultCode(Enum):
    """
    7-zip 状态返回码定义

    0 No error
    1 Warning (Non fatal error(s)). For example, one or more files were locked by some other application,
        so they were not compressed.
    2 Fatal error
    7 Command line error
    8 Not enough memory for operation
    255 User stopped the process
    """

    NO_ERROR = (0, "成功")
    WARNING = (1, "警告(非致命错误)")
    FATAL_ERROR = (2, "致命错误")
    COMMAND_LINE_ERROR = (7, "命令行错误")
    NOT_ENOUGH_MEMORY_ERROR = (8, "没有足够的内存进行操作")
    USER_STOPPED = (255, "用户停止进程")

    # 扩展状态码
    UNKNOWN = (-1, "未知")
    # Headers Error in encrypted archive.
    HEADERS_ERROR = (-2, "加密压缩包头部错误")

    @property
    def tip(self):
        """
        状态码提示信息
        """
        return self.value[1]

    @classmethod
    def init(cls, code: int):
        """
        根据状态码初始化 ResultCode

        :param code: 状态码
        """
        for item in cls:
            if item.value[0] == code:
                return item

        return ResultCode.UNKNOWN


class Attr(BaseModel):
    """
    压缩包属性
    """

    model_config = ConfigDict(extra="allow")

    type: str = ""
    volumes: Optional[int] = None
    multivolume: Optional[bool] = None
    volume_index: Optional[int] = None
    characteristics: Optional[str] = None


class Result(BaseModel):
    """
    7zip 命令行结果
    """

    # 命令行输出结果
    message: str
    # 传入路径
    file_path: Path
    # 传入密码
    password: str
    # 状态码
    code: ResultCode

    # 是否是分卷压缩包
    is_volume: bool = False

    # 压缩包信息
    attr: Attr = Attr()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 解析压缩包信息
        self._parse_infos()

    def _update_info(self, key: str, value: str):
        """
        更新压缩包信息

        :param key: 参数名称
        :param value: 参数值
        """
        format_value: any = value

        if key == "type":
            if value.lower() == "split":
                self.is_volume = True
                return

        elif key == "multivolume":
            format_value = value == "+"
            if format_value:
                self.is_volume = True

        elif key == "volumes":
            format_value = int(value)
            if format_value > 1:
                self.is_volume = True

        elif key == "volume_index":
            format_value = int(value)
            self.is_volume = True

        setattr(self.attr, key, format_value)

    def _parse_infos(self):
        """
        解析压缩包信息
        """
        pattern = r"^([a-zA-Z ]+)\s+=\s+(.+)"
        groups: List[Tuple[str, str]] = re.findall(pattern, self.message, re.M)
        for key, value in groups:
            self._update_info(key.replace(" ", "_").lower(), value.strip())


class ExtractResult(Result):
    """
    7zip 解压结果
    """

    pass


class FileInfo(BaseModel):
    """
    压缩包内文件信息
    """

    date_time: Optional[str] = None
    #  D:文件夹 R:只读文件 H:隐藏文件 S:系统文件 A:普通文件
    attr: Literal["D", "R", "H", "S", "A", ""]
    size: Optional[int] = None
    compressed: Optional[int] = None
    path: Path

    @property
    def is_dir(self) -> bool:
        """
        是否是文件夹
        """
        return self.attr == "D"


class ListResult(Result):
    # 文件列表
    files: List[FileInfo] = []

    @property
    def volume_main_path(self) -> Path:
        """
        主分卷文件路径
        """
        return self.volume_paths[0]

    @computed_field
    @property
    def volume_paths(self) -> List[Path]:
        """
        所有分卷文件路径
        """
        if not self.is_volume:
            return [self.file_path]

        # 文件名不含后缀
        stem = self.file_path.stem
        name = self.file_path.name
        parent = self.file_path.parent
        suffix = self.file_path.suffix

        archive_type = self.attr.type.lower()

        def loop_search(name_callback: Callable[[int], str]) -> List[Path]:
            """
            循环搜索分卷文件

            :param name_callback: 名称回调函数 (index: int) -> str
            """
            paths: List[Path] = []
            index = 1
            while True:
                volume_path = parent / name_callback(index)
                if not volume_path.exists():
                    break
                paths.append(volume_path)
                index += 1
            return paths

        volume_paths: List[Path] = []

        # 处理 .001 .01 之类为后缀的分卷
        if re.match(r"\.0+[1-9]\d*$", suffix):
            suffix_len = len(suffix) - 1
            volume_paths += loop_search(lambda i: f"{stem}.{str(i).zfill(suffix_len)}")

        # 处理 zip 相关的压缩包
        # 处理 .zip .z01 之类为后缀的压缩包
        elif archive_type == "zip":
            volume_paths.append(parent / f"{stem}.zip")
            volume_paths += loop_search(lambda i: f"{stem}.z{str(i).zfill(2)}")

        # 处理 rar 相关的压缩包
        elif "rar" in archive_type:
            # 处理 .part1.rar 之类为后缀的压缩包
            part_pattern = r"(.+)\.part\d+\.rar$"
            if re.match(part_pattern, name):
                base_name = re.sub(part_pattern, r"\1", name)
                volume_paths += loop_search(lambda i: f"{base_name}.part{i}.rar")

        # todo: 处理其他分卷压缩包类型

        if len(volume_paths) == 0:
            volume_paths.append(self.file_path)

        return [p for p in volume_paths if p.exists()]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 解析文件列表
        self._parse_files()

    def _parse_files(self):
        """
        解析压缩包文件列表

        大致格式如下:

        ```txt
           Date      Time    Attr         Size   Compressed  Name
        ------------------- ----- ------------ ------------  ------------------------
        2022-11-11 01:04:14 D....        0                   image
        2022-11-11 01:04:14 ....A        56792    201084528  image\a.svg
        ------------------- ----- ------------ ------------  ------------------------
        ```
        """
        pattern = r"((?:(?:-+\s+){4})+(?:-+))([\s\S]+?)(?:(?:-+\s+){5})+"
        groups: List[Tuple[str, str]] = re.findall(pattern, self.message, re.M)

        if len(groups) == 0:
            return

        # 获取列开始位置
        # 0                   20    26           39            53
        # ------------------- ----- ------------ ------------  ------------------------
        col_index = [s.start() for s in re.finditer(r"-{4,}", groups[0][0], re.M)]

        lines: List[str] = groups[0][1].split(os.linesep)

        for line in lines:
            if len(line) < col_index[4]:
                continue

            # 时间
            d = line[col_index[0] : col_index[1]].strip()
            date_time = None if d == "" else d

            # 文件属性 D.... => D
            attr = line[col_index[1] : col_index[2]].strip().replace(".", "")

            # 大小
            s = line[col_index[2] : col_index[3]].strip()
            size = None if s == "" else int(s)

            # 压缩大小
            c = line[col_index[3] : col_index[4]].strip()
            compressed = None if c == "" else int(c)

            # 文件名
            name = line[col_index[4] :].strip()

            file = FileInfo(
                date_time=date_time,
                attr=attr,
                size=size,
                compressed=compressed,
                path=Path(name),
            )
            self.files.append(file)


class TestResult(Result):
    """
    测试结果
    """

    pass
