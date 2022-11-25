from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Any

import utils
from util7zip import AnalysisInfo


class UnpackException(Exception):
    """
    异常
    """
    pass


class KeysValuesEnum(Enum):

    @classmethod
    def keys(cls):
        return [item.name for item in cls]

    @classmethod
    def values(cls):
        return [item.value for item in cls]

    @classmethod
    def init_by_key(cls, key: str):
        for item in cls:
            # 忽略大小写
            if key.upper() == item.name.upper():
                return item


class PackFileStatusEnum(KeysValuesEnum):
    """
    压缩包处理状态
    """

    # 扫描
    SCAN = '扫描收录'
    # 改名
    RENAME = '修改名字'
    RENAME_FAIL = '改名失败'
    UN_RENAME = '未改名字'
    # 过滤
    FILTER_INCLUDE = '过滤包含'
    FILTER_EXCLUDE = '过滤排除'
    # 识别
    ANALYSIS_SUCCESS = '识别成功'
    ANALYSIS_FAIL = '识别失败'
    ANALYSIS_SUCCESS_SPLIT = '识别成功(分卷子卷)'
    # 测试
    TEST_SUCCESS = '测试成功'
    TEST_FAIL = '测试失败'
    # 解压
    UNPACK_SUCCESS = '解压成功'
    UNPACK_FAIL = '解压失败'


@dataclass
class PackFile(object):
    """
    压缩包信息
    """

    # 识别信息
    analysis_info: AnalysisInfo = field(init=False, default=None)
    # 改名历史
    name_history: List[str] = field(init=False, default_factory=list)
    # 状态历史
    status_history: List[PackFileStatusEnum] = field(init=False, default_factory=list)
    # 异常历史
    error_history: List[Exception] = field(init=False, default_factory=list)

    # 密码
    password: str = field(init=False, default='')
    # 解压路径
    unpack_path: str = field(default='')

    # 文件名称
    name: str = ''
    # 文件父路径
    path: str = ''
    # 文件状态
    status: PackFileStatusEnum = None
    # 是否已经删除
    is_del: bool = False
    # 是否获取到密码
    is_has_password: bool = False

    def __setattr__(self, key: str, value: Any):
        # 拦截 改名历史
        if key == 'name' and value != '':
            self.name_history.append(value)
        # 拦截 状态历史
        elif key == 'status' and value is not None:
            self.status_history.append(value)
        # 拦截 设置密码
        elif key == 'password':
            self.is_has_password = True
        object.__setattr__(self, key, value)

    def get_file_full_path(self) -> str:
        return str(Path(self.path, self.name))

    def is_has_status(self, status: List[PackFileStatusEnum]) -> bool:
        # 是否经历过某些状态
        return len([status_item for status_item in self.status_history if status_item in status]) > 0

    @property
    def is_has_error(self) -> bool:
        return len(self.error_history) > 0

    @property
    def error_info_list(self) -> List[str]:
        return [str(error) for error in self.error_history]

    def __str__(self):
        res = [f'[{self.status.value}]', f' 文件名:[{self.name}]']

        if self.is_has_status([PackFileStatusEnum.TEST_SUCCESS, PackFileStatusEnum.UNPACK_SUCCESS]):
            res.append(f' 密码:[{self.password}]')

        if self.is_has_status([PackFileStatusEnum.UNPACK_SUCCESS]):
            res.append(f' 是否已经删除:[{utils.bool_map(self.is_del)}]')

        if self.is_has_status([PackFileStatusEnum.ANALYSIS_SUCCESS, PackFileStatusEnum.ANALYSIS_SUCCESS_SPLIT]):
            res.append(f' 文件信息:[{self.analysis_info}]')

        res.append(f' 存放路径:[{self.path}]')

        if self.is_has_status([PackFileStatusEnum.UNPACK_SUCCESS]):
            res.append(f' 解压路径:[{self.unpack_path}]')

        if self.is_has_status([PackFileStatusEnum.RENAME]):
            res.append(f' 改名记录:[{"->".join(self.name_history)}]')

        res.append(f' 状态记录:[{"->".join([status.value for status in self.status_history])}]')

        if self.is_has_error:
            res.append(f' 存在处理异常,异常如下:[{self.error_info_list}]')

        return ''.join(res)


class TimeDuration(object):
    """
    历时时间
    """

    _start_time: datetime = None
    _end_time: datetime = None

    def start(self) -> None:
        # 开始计时
        self._start_time = datetime.now()

    def end(self) -> None:
        # 结束计时
        self._end_time = datetime.now()

    @property
    def duration(self) -> int:
        # 获取时间差(秒)
        return 0 if self._start_time is None or self._end_time is None else \
            (self._end_time - self._start_time).seconds


@dataclass
class UnpackStat(object):
    """
    解压统计
    """

    scan_duration: TimeDuration = TimeDuration()
    rename_duration: TimeDuration = TimeDuration()
    filter_duration: TimeDuration = TimeDuration()
    test_duration: TimeDuration = TimeDuration()
    analysis_duration: TimeDuration = TimeDuration()
    unpack_duration: TimeDuration = TimeDuration()
    clear_duration: TimeDuration = TimeDuration()

    scan_count: int = 0
    rename_count: int = 0
    filter_exclude_count: int = 0
    analysis_fail_count: int = 0
    analysis_success_split_count: int = 0
    test_fail_count: int = 0
    unpack_fail_count: int = 0
    unpack_success_count: int = 0
    unpack_error_count: int = 0

    @classmethod
    def get_status_info(cls):
        return '\n'.join([
            f'扫描时长:{cls.scan_duration.duration}秒',
            f'改名时长:{cls.rename_duration.duration}秒',
            f'过滤时长:{cls.filter_duration.duration}秒',
            f'测试时长:{cls.test_duration.duration}秒',
            f'识别时长:{cls.analysis_duration.duration}秒',
            f'解压时长:{cls.unpack_duration.duration}秒',
            f'清理时长:{cls.clear_duration.duration}秒',
            utils.str_rep('-', 100),
            f'扫描文件总数:{cls.scan_count}',
            f'文件改名总数:{cls.rename_count}',
            f'过滤排除总数:{cls.filter_exclude_count}',
            f'识别失败总数:{cls.analysis_fail_count}',
            f'识别成功(分卷子卷)总数:{cls.analysis_success_split_count}',
            f'测试失败总数:{cls.test_fail_count}',
            f'解压失败总数:{cls.unpack_fail_count}',
            f'解压成功总数:{cls.unpack_success_count}',
            f'解压过程中异常总数:{cls.unpack_error_count}',
        ])
