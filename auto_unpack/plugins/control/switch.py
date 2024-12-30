import logging
from typing import List, Literal, Optional, Union

from pydantic import Field

from auto_unpack.plugin import OutputPluginConfig, Plugin
from auto_unpack.plugins.control.filter import (
    CTimeFilter,
    Filter,
    GlobFilter,
    MTimeFilter,
    SizeFilter,
)
from auto_unpack.store import Context

logger = logging.getLogger(__name__)


class Case(Filter):
    """
    数据分支条件
    """

    # 分支上下文
    save_key: str = Field(description="分支上下文")


class SizeCase(SizeFilter, Case):
    """
    大小分支条件
    """

    pass


class GlobCase(GlobFilter, Case):
    """
    文件 glob 表达式分支条件
    """

    pass


class CTimeCase(CTimeFilter, Case):
    """
    创建时间分支条件
    """

    pass


class MTimeCase(MTimeFilter, Case):
    """
    修改时间分支条件
    """

    pass


Case_Type = Union[SizeCase, GlobCase, CTimeCase, MTimeCase]


class SwitchPluginConfig(OutputPluginConfig):
    """
    条件分支上下文插件配置
    """

    name: Literal["switch"] = Field(default="switch", description="条件分支上下文插件")
    cases: List[Case_Type] = Field(default=[], description="分支条件(默认: [])")
    default_key: Optional[str] = Field(
        default=None, description="未匹配到分支条件时上下文 key(默认: null)"
    )


class SwitchPlugin(Plugin[SwitchPluginConfig]):
    """
    条件分支上下文插件

    作用: 依据条件对当前上下文数据分组, 并保存到新上下文
    """

    name: str = "switch"

    def execute(self):
        context = self.load_context()

        file_datas = context.file_datas

        for ca in self.config.cases:
            # 分支条件匹配
            case_file_datas = ca.filter(file_datas)
            # 剔除已保存到新上下文的分支条件匹配数据
            file_datas = [fd for fd in file_datas if fd not in case_file_datas]
            # 保存到新上下文
            self.save_context(Context(file_datas=case_file_datas), ca.save_key)

        if self.config.default_key is not None:
            # 未匹配到分支条件的数据
            self.save_context(Context(file_datas=file_datas), self.config.default_key)
