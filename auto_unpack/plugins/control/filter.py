import logging
import operator
from typing import Any, Callable, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, field_validator

from auto_unpack.plugin import HandlePluginConfig, Plugin
from auto_unpack.store import Context, FileData, paths_excludes, paths_includes

logger = logging.getLogger(__name__)


class Filter(BaseModel):
    """
    过滤
    """

    def filter(self, file_datas: List[FileData]) -> List[FileData]:
        """
        过滤文件数据
        """
        return file_datas


operator_map: Dict[str, Callable[[Any, Any], bool]] = {
    '<': operator.lt,
    '>': operator.gt,
    '<=': operator.le,
    '>=': operator.ge,
    '==': operator.eq,
    '!=': operator.ne
}

unit_map: Dict[str, int] = {
    'b': 1,
    'kb': 1024,
    'mb': 1024 * 1024,
    'gb': 1024 * 1024 * 1024,
    'tb': 1024 * 1024 * 1024 * 1024
}


class SizeFilter(Filter):
    """
    文件大小过滤
    """
    mode: Literal['size'] = 'size'
    # 文件大小限制
    size: float
    # 大小比较运算符
    operator: Literal['<', '>', '<=', '>=', '==', '!='] = '>='
    # 单位 默认 mb
    unit: Literal['b', 'kb', 'mb', 'gb', 'tb'] = 'mb'

    @field_validator('unit', mode='before')
    @classmethod
    def validate_unit(cls, v: Any):
        return v.lower()

    @field_validator('size')
    @classmethod
    def validate_size(cls, v: Any):
        if v <= 0:
            raise ValueError(f"Size must be greater than 0, but got {v}.")
        return v

    def filter(self, file_datas: List[FileData]) -> List[FileData]:
        include_file_datas = []

        operator_func = operator_map[self.operator]
        size = self.size * unit_map[self.unit]

        for f in file_datas:
            if operator_func(f.path.stat().st_size, size):
                include_file_datas.append(f)

        return include_file_datas


class GlobFilter(Filter):
    """
    文件 glob 表达式过滤
    """
    mode: Literal['glob'] = 'glob'
    # 包含的文件 glob 表达式
    includes: List[str] = ["**/*"]
    # 排除的文件 glob 表达式
    excludes: List[str] = []

    def filter(self, file_datas: List[FileData]) -> List[FileData]:
        include_file_datas = paths_includes(
            file_datas, self.includes)
        return paths_excludes(
            include_file_datas, self.excludes)


Filter_Type = Union[SizeFilter, GlobFilter]


class FilterPluginConfig(HandlePluginConfig):
    """
    过滤插件配置
    """
    # 包含的文件 glob 表达式
    includes: List[str] = ["**/*"]
    # 排除的文件 glob 表达式
    excludes: List[str] = []
    # 排除掉的上下文 key
    exclude_key: Optional[str] = None
    # 筛选规则
    rules: List[Filter_Type] = []


class FilterPlugin(Plugin[FilterPluginConfig]):
    """
    过滤插件

    作用: 过滤文件数据, 保留符合条件的文件数据
    """
    name: str = "filter"

    def execute(self):
        context = self.load_context()

        filters: List[Filter_Type] = [
            # 过渡 glob 规则, 兼容旧配置
            # feature: 后续大版本升级应该移除
            GlobFilter(
                includes=self.config.includes,
                excludes=self.config.excludes
            ),
            *self.config.rules
        ]

        include_file_datas = context.file_datas

        for filter in filters:
            include_file_datas = filter.filter(include_file_datas)

        self.save_context(Context(file_datas=include_file_datas))

        logger.info(f"Matched {len(include_file_datas)} files.")

        if self.config.exclude_key is not None:
            exclude_file_datas = [
                f for f in context.file_datas if f not in include_file_datas]
            self.save_context(
                Context(file_datas=exclude_file_datas), self.config.exclude_key)
