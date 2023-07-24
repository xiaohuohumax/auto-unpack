import re
from dataclasses import dataclass, field
from enum import Enum
from typing import List

from .utils import bool_map


class Util7zResCodeEnum(Enum):
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
    def status_tip(self):
        return self.value[1]

    @classmethod
    def init(cls, res_code: int):
        for item in cls:
            if item.value[0] == res_code:
                return item

        return Util7zResCodeEnum.UNKNOWN

    def __str__(self):
        return f'{self.value[0]},{self.value[1]}'


@dataclass(init=False)
class Util7zRes:
    # 状态
    status: Util7zResCodeEnum = Util7zResCodeEnum.UNKNOWN
    # 返回信息
    result_info: str = ''

    def __init__(self, status: int, result_info: str):
        self.status = Util7zResCodeEnum.init(status)
        self.result_info = result_info

    def __str__(self):
        analysis_res_format = self.result_info.replace("\r\n", '')
        return ''.join([
            f'状态码:({self.status})',
            f' 返回信息:{analysis_res_format}'
        ])


@dataclass(init=False)
class Util7zUnpackRes(Util7zRes):
    """
    解压返回结果
    """
    pass


@dataclass(init=False)
class Util7zTestRes(Util7zRes):
    """
    测试返回结果
    """
    pass


@dataclass
class PackInfoFile:
    """
    压缩包文件信息
    """

    r"""
       Date      Time    Attr         Size   Compressed  Name
    ------------------- ----- ------------ ------------  ------------------------
    2022-11-11 01:04:14 ....A        56792    201084528  image\1.jpg
    2022-11-11 01:04:14 D....        0                   image
    """

    time: str = ''
    attr: str = ''
    size: int = ''
    compressed: int = ''
    name: str = ''

    @property
    def path_level(self) -> int:
        """
        文件所在层数 1 开始
        :return: 层数
        """
        return len(self.name.split("\\"))

    @property
    def is_folder(self) -> bool:
        """
        是否是文件夹

        DRHSA => D:文件夹 R:只读文件 H:隐藏文件 S:系统文件 A:普通文件
        文件夹 D....
        文件   ....A
        :return: 是否是文件夹
        """
        return self.attr.startswith('D')


@dataclass
class AnalysisInfo:
    """
    压缩包信息
    """

    path: str = ''
    type: str = ''
    method: str = None

    physical_size: int = 0
    headers_size: int = 0
    blocks: int = 0
    # 分卷数量
    volumes: int = None
    # 分卷下标
    volume_index: int = None

    offset: int = None

    solid: bool = None
    encrypted: bool = None
    # 是否分卷
    multivolume: bool = None

    # 压缩包文件信息
    file_list: List[PackInfoFile] = field(default_factory=list)

    @property
    def is_split(self) -> bool:
        # 判断是否是分卷压缩
        if self.multivolume is not None:
            return self.multivolume

        # 存在分卷数
        if self.volumes is not None:
            return True

        if self.offset is not None:
            return True

        # 存在分卷下标
        if self.volume_index is not None:
            return True

        return False

    @property
    def is_split_item(self) -> bool:
        # 是否是分卷 子卷
        if self.is_split:
            # 存在分卷下标 且 > 0
            if self.volume_index is not None and self.volume_index > 0:
                return True
            if self.offset is not None:
                return True
        return False

    def set_attr(self, key: str, value: str) -> None:
        """
        设置压缩包信息 (其他参数可自行扩展补充)
        :param key: 信息名
        :param value: 信息值
        :return: None
        """
        if key in ['path', 'type', 'method']:
            setattr(self, key, value)
        elif key in ['physical_size', 'headers_size', 'blocks', 'volume_index', 'volumes']:
            setattr(self, key, int(value))
        elif key in ['solid', 'encrypted', 'multivolume']:
            setattr(self, key, value == '+')

    @property
    def root_file_count(self) -> int:
        """
        压缩包根目录文件数(包含文件夹)
        :return 目录文件数(包含文件夹)
        """
        return len([item for item in self.file_list if item.path_level == 1])

    @property
    def file_list_count(self) -> int:
        """
        压缩包中文件总数(包含文件夹)
        :return 文件总数(包含文件夹)
        """
        return len(self.file_list)

    @property
    def file_count(self) -> int:
        """
        压缩包中文件总数
        :return 文件总数
        """
        return len([item.attr for item in self.file_list if not item.is_folder])

    @property
    def folder_count(self) -> int:
        """
        压缩包中文件夹总数
        :return 文件夹总数
        """
        return len([item.attr for item in self.file_list if item.is_folder])

    def __str__(self):
        res = [f'压缩类型:{self.type}', f', 是否分卷压缩:{bool_map(self.is_split)}']

        if self.is_split:
            if self.volume_index == 0:
                res.append(f', 分卷总数:{self.volumes}')
            res.append(f', 分卷下标:{self.volume_index}')

        res.append(f', 物理大小:{self.physical_size}')
        res.append(f', 头部大小:{self.headers_size}')

        if self.file_count > 0:
            res.append(f', 文件总数:{self.file_count}')
        if self.folder_count > 0:
            res.append(f', 文件夹总数:{self.folder_count}')

        if self.method is not None:
            res.append(f', 方式:{self.method}')

        return ''.join(res)


@dataclass(init=False, frozen=True)
class RePattern:
    """
    7zip返回结果筛选正则
    """

    # key = value
    pattern_pack_attr_item: str = r'^([a-zA-Z ]+)\s+=\s+(.+)$'

    # 2022-11-16 00:46:07 ....A      9684371               images\1.png
    # 2022-11-21 20:12:12 D....            0            0  images
    pattern_file_infos: str = r'^(\d{4}(?:-\d{2}){2}\s+(?:\d{2}:){2}\d{2})\s+([A-Z.]+)\s+(\d+)\s+(?:(\d+)\s+)?(.*)$'


@dataclass(init=False)
class Util7zAnalysisRes(Util7zRes):
    """
    识别返回结果
    """

    analysis_info: AnalysisInfo = None

    def _analysis_info_init(self, result_info: str) -> None:
        # 解析压缩包信息
        # 获取压缩包信息[(key , value), ... ]
        pattern_pack_attr_item = re.findall(RePattern.pattern_pack_attr_item, result_info, re.M)

        # 设置参数 Physical Size = 10000 => { 'physical_size': '10000'  } 存在相同key 则以最后一个为准
        [
            self.analysis_info.set_attr(str(key).replace(' ', '_').lower().strip(), str(value).strip())
            for key, value in pattern_pack_attr_item
        ]

        # 获取全部文件信息
        file_infos = re.findall(RePattern.pattern_file_infos, result_info, re.M)

        [
            self.analysis_info.file_list.append(
                PackInfoFile(time=item[0], attr=item[1], size=int(item[2]),
                             compressed=int(item[3]) if item[3] != '' else None, name=item[4])
            )
            for item in file_infos
        ]

    def __init__(self, status: int, result_info: str):
        super(Util7zAnalysisRes, self).__init__(status, result_info)

        self.analysis_info = AnalysisInfo()

        if self.status == Util7zResCodeEnum.NO_ERROR:
            self._analysis_info_init(result_info)
