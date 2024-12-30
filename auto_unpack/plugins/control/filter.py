import logging
import operator
from datetime import datetime
from typing import Any, Callable, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, field_validator

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
    "<": operator.lt,
    ">": operator.gt,
    "<=": operator.le,
    ">=": operator.ge,
    "==": operator.eq,
    "!=": operator.ne,
}

unit_map: Dict[str, int] = {
    "b": 1,
    "kb": 1024,
    "mb": 1024 * 1024,
    "gb": 1024 * 1024 * 1024,
    "tb": 1024 * 1024 * 1024 * 1024,
}


class SizeFilter(Filter):
    """
    文件大小过滤
    """

    mode: Literal["size"] = Field(default="size", description="文件大小过滤")
    size: float = Field(
        description="文件大小限制",
        json_schema_extra={
            "minimum": 0,
        },
    )
    operator: Literal["<", ">", "<=", ">=", "==", "!="] = Field(
        default=">=", description="大小比较运算符(默认: >=)"
    )
    unit: Literal["b", "kb", "mb", "gb", "tb"] = Field(
        default="mb", description="单位(默认: mb)"
    )

    @field_validator("unit", mode="before")
    @classmethod
    def validate_unit(cls, v: Any):
        return v.lower()

    @field_validator("size")
    @classmethod
    def validate_size(cls, v: Any):
        if v < 0:
            raise ValueError(f"Size must be greater than or equal to 0, but got {v}.")
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
    文件名过滤
    """

    mode: Literal["glob"] = Field(default="glob", description="文件名过滤(glob 表达式)")
    includes: List[str] = Field(
        default=["**/*"], description="包含的文件路径列表(glob 表达式, 默认: [**/*])"
    )
    excludes: List[str] = Field(
        default=[], description="排除的文件路径列表(glob 表达式, 默认: [])"
    )

    def filter(self, file_datas: List[FileData]) -> List[FileData]:
        include_file_datas = paths_includes(file_datas, self.includes)
        return paths_excludes(include_file_datas, self.excludes)


class TimeFilter(Filter):
    """
    时间过滤
    """

    mode: Literal["ctime"] = Field(default="ctime", description="创建时间过滤")
    time: datetime = Field(
        description="时间限制(格式: RFC3339)\n例如：2022-01-01T00:00:00Z"
    )
    operator: Literal["<", ">", "<=", ">=", "==", "!="] = Field(
        default=">=", description="大小比较运算符(默认: >=)"
    )

    def filter(self, file_datas: List[FileData]) -> List[FileData]:
        include_file_datas = []

        operator_func = operator_map[self.operator]

        for f in file_datas:
            if operator_func(self.operator_left_time(f), self.time.timestamp()):
                include_file_datas.append(f)

        return include_file_datas

    def operator_left_time(self, f: FileData) -> float:
        raise NotImplementedError()


class CTimeFilter(TimeFilter):
    """
    创建时间过滤
    """

    mode: Literal["ctime"] = Field(default="ctime", description="创建时间过滤")

    def operator_left_time(self, f: FileData) -> float:
        return f.path.stat().st_ctime


class MTimeFilter(TimeFilter):
    """
    最后修改时间过滤
    """

    mode: Literal["mtime"] = Field(default="mtime", description="最后修改时间过滤")

    def operator_left_time(self, f: FileData) -> float:
        return f.path.stat().st_mtime


Filter_Type = Union[SizeFilter, GlobFilter, CTimeFilter, MTimeFilter]


class FilterPluginConfig(HandlePluginConfig):
    """
    过滤插件配置
    """

    name: Literal["filter"] = Field(default="filter", description="过滤插件")
    # major_todo: 3.x.x 移除 includes 和 excludes 字段
    includes: List[str] = Field(
        default=["**/*"],
        description="[已废弃]包含的文件路径列表(glob 表达式, 默认: [**/*])",
    )
    excludes: List[str] = Field(
        default=[], description="[已废弃]排除的文件路径列表(glob 表达式, 默认: [])"
    )
    exclude_key: Optional[str] = Field(
        default=None, description="排除掉的上下文(默认: null)"
    )
    rules: List[Filter_Type] = Field(default=[], description="筛选规则(默认: [])")


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
            GlobFilter(includes=self.config.includes, excludes=self.config.excludes),
            *self.config.rules,
        ]

        include_file_datas = context.file_datas

        for filter in filters:
            include_file_datas = filter.filter(include_file_datas)

        self.save_context(Context(file_datas=include_file_datas))

        logger.info(f"Matched {len(include_file_datas)} files.")

        if self.config.exclude_key is not None:
            exclude_file_datas = [
                f for f in context.file_datas if f not in include_file_datas
            ]
            self.save_context(
                Context(file_datas=exclude_file_datas), self.config.exclude_key
            )
