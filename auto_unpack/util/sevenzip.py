import logging
import os
import re
import subprocess
from enum import Enum
from pathlib import Path
from typing import Callable, List, Literal, Optional, Tuple, TypeVar

from pydantic import BaseModel, computed_field

logger = logging.getLogger(__name__)


def exec_cmd(cmds: List[str], decode: str = "utf-8") -> Tuple[int, str]:
    """
    调用命令行

    :param decode: 编码格式
    :param cmd: 命令
    :return: 状态码，返回信息
    """
    with subprocess.Popen(' '.join(cmds), stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          shell=True) as proc:
        info, _ = proc.communicate()
        return proc.returncode, info.decode(decode, errors='ignore')


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

    NO_ERROR = (0, '成功')
    WARNING = (1, '警告(非致命错误)')
    FATAL_ERROR = (2, '致命错误')
    COMMAND_LINE_ERROR = (7, '命令行错误')
    NOT_ENOUGH_MEMORY_ERROR = (8, '没有足够的内存进行操作')
    USER_STOPPED = (255, '用户停止进程')

    UNKNOWN = (-1, '未知')

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
    attr: Literal['D', 'R', 'H', 'S', 'A', '']
    size: Optional[int] = None
    compressed: Optional[int] = None
    path: Path

    @property
    def is_dir(self) -> bool:
        """
        是否是文件夹
        """
        return self.attr == 'D'


class ListResult(Result):

    # 文件列表
    files: List[FileInfo] = []
    # 是否是分卷压缩包
    is_volume: bool = False

    # 压缩包信息
    # 其他自行扩展
    _l_type: str = ''
    _l_volumes: Optional[int] = None
    _l_multivolume: Optional[bool] = None
    _l_volume_index: Optional[int] = None
    ...

    @computed_field
    @property
    def type(self) -> str:
        """
        压缩包类型
        """
        return self._l_type

    @computed_field
    @property
    def volumes(self) -> Optional[int]:
        """
        压缩包分卷数
        """
        return self._l_volumes

    @property
    def volume_index(self) -> Optional[int]:
        """
        当前分卷索引
        """
        return self._l_volume_index

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

        archive_type = self._l_type.lower()

        def loop_search(name_callback: Callable[[int], str]) -> List[Path]:
            """
            循环搜索分卷文件

            :param name_callback: 名称回调函数 (index: int) -> str
            """
            paths: List[Path] = []
            index = 1
            while True:
                volume_path = parent/name_callback(index)
                if not volume_path.exists():
                    break
                paths.append(volume_path)
                index += 1
            return paths

        volume_paths: List[Path] = []

        # 处理 .001 .01 之类为后缀的分卷
        if re.match(r'\.0+[1-9]\d*$', suffix):
            suffix_len = len(suffix) - 1
            volume_paths += loop_search(
                lambda i: f'{stem}.{str(i).zfill(suffix_len)}')

        # 处理 zip 相关的压缩包
        # 处理 .zip .z01 之类为后缀的压缩包
        elif archive_type == 'zip':
            volume_paths.append(parent / f'{stem}.zip')
            volume_paths += loop_search(lambda i: f'{stem}.z{str(i).zfill(2)}')

        # 处理 rar 相关的压缩包
        elif 'rar' in archive_type:
            # 处理 .part1.rar 之类为后缀的压缩包
            part_pattern = r'(.+)\.part\d+\.rar$'
            if re.match(part_pattern, name):
                base_name = re.sub(part_pattern, r'\1', name)
                volume_paths += loop_search(
                    lambda i: f'{base_name}.part{i}.rar')

        # todo: 处理其他分卷压缩包类型

        if len(volume_paths) == 0:
            volume_paths.append(self.file_path)

        return [p for p in volume_paths if p.exists()]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.code == ResultCode.NO_ERROR:
            # 解析压缩包信息
            self._parse_infos()
            # 解析文件列表
            self._parse_files()

    def _update_info(self, key: str, value: str):
        """
        更新压缩包信息

        :param key: 参数名称
        :param value: 参数值
        """
        format_key = '_l_' + key
        format_value: any = value

        if key == 'type':
            if value.lower() == 'split':
                self.is_volume = True
                return

        elif key == 'multivolume':
            format_value = value == '+'
            if format_value:
                self.is_volume = True

        elif key == 'volumes':
            format_value = int(value)
            if format_value > 1:
                self.is_volume = True

        elif key == 'volume_index':
            format_value = int(value)
            self.is_volume = True

        setattr(self, format_key, format_value)

    def _parse_infos(self):
        """
        解析压缩包信息
        """
        pattern = r'^([a-zA-Z ]+)\s+=\s+(.+)'
        groups: List[Tuple[str, str]] = re.findall(pattern, self.message, re.M)
        for key, value in groups:
            self._update_info(key.replace(' ', '_').lower(), value.strip())

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
        pattern = r'((?:(?:-+\s+){4})+(?:-+))([\s\S]+?)(?:(?:-+\s+){5})+'
        groups: List[Tuple[str, str]] = re.findall(pattern, self.message, re.M)

        if len(groups) == 0:
            return

        # 获取列开始位置
        # 0                   20    26           39            53
        # ------------------- ----- ------------ ------------  ------------------------
        col_index = [s.start()
                     for s in re.finditer(r'-{4,}', groups[0][0], re.M)]

        lines: List[str] = groups[0][1].split(os.linesep)

        for line in lines:
            if len(line) < col_index[4]:
                continue

            # 时间
            d = line[col_index[0]:col_index[1]].strip()
            date_time = None if d == '' else d

            # 文件属性 D.... => D
            attr = line[col_index[1]:col_index[2]].strip().replace('.', '')

            # 大小
            s = line[col_index[2]:col_index[3]].strip()
            size = None if s == '' else int(s)

            # 压缩大小
            c = line[col_index[3]:col_index[4]].strip()
            compressed = None if c == '' else int(c)

            # 文件名
            name = line[col_index[4]:].strip()

            file = FileInfo(date_time=date_time, attr=attr,
                            size=size, compressed=compressed, path=Path(name))
            self.files.append(file)


class TestResult(Result):
    """
    测试结果
    """
    pass


T = TypeVar('T', bound=Result)


def load_sevenzip_lib() -> Path:
    """
    加载 7zip 库


    :return: 7zip 库路径
    """
    # todo: 适配其他平台
    lib_path = Path(__file__).parent/'lib/win/7z.exe'
    if not lib_path.exists():
        raise FileNotFoundError(f'7-zip lib not found: {lib_path}')
    return lib_path


class SevenZipUtil:
    """
    7zip 工具类
    """

    # 7zip 可执行文件路径
    _lib_path: Path = load_sevenzip_lib()

    @classmethod
    def exec(cls, sub: str, options: List[str], file_path: Path, password: str = '', result_class: T = Result) -> T:
        """
        执行 7zip 命令

        :param sub: 子命令
        :param options: 命令选项
        :param file_path: 压缩包路径
        :param password: 密码
        :param result_class: 结果类
        :return: 结果
        """
        cmds = [
            str(cls._lib_path),
            sub,
            f'"{file_path}"',
            f'-p"{password}"',
            '-y',
            *options
        ]
        code, message = exec_cmd(cmds)
        result_code = ResultCode.init(code)

        # ResultCode.FATAL_ERROR 时, 有可能出现 Unexpected end of archive 存档的意外结束
        # 虽然可以读取压缩包信息, 但是命令执行报错 2
        # 常出实现于分卷未能正常链接, 导致执行失败, 暂不处理
        # zipx, zx01, e01 等等

        return result_class(message=message, file_path=file_path, password=password, code=result_code)

    @classmethod
    def extract(cls, file_path: Path, password: str = '', output_dir: Path = '', overwrite: str = 't',
                keep_dir: bool = True) -> ExtractResult:
        """
        解压 7zip 压缩包

        :param file_path: 压缩包路径
        :param password: 密码
        :param output_dir: 输出目录
        :param overwrite: 覆盖模式 a/s/t/u
        :param keep_dir: 是否保留目录结构
        :return: 解压结果
        """
        sub = 'x' if keep_dir else 'e'
        options = [
            f'-ao{overwrite}',
            f'-o"{output_dir}"',
        ]
        return cls.exec(sub, options, file_path, password, ExtractResult)

    @classmethod
    def list(cls, file_path: Path, password: str = '') -> ListResult:
        """
        列出 7zip 压缩包信息

        :param file_path: 压缩包路径
        :param password: 密码
        :return: 压缩包信息
        """
        return cls.exec('l', [], file_path, password, ListResult)

    @classmethod
    def test(cls, file_path: Path, password: str = '') -> TestResult:
        """
        测试 7zip 压缩包是否完整

        :param file_path: 压缩包路径
        :param password: 密码
        :return: 测试结果
        """
        return cls.exec('t', [], file_path, password, ListResult)
