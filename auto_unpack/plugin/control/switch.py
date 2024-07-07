import logging
from typing import List, Optional

from pydantic import BaseModel

from auto_unpack.plugin import OutputPluginConfig, Plugin
from auto_unpack.store import Context, paths_excludes, paths_includes

logger = logging.getLogger(__name__)


class Case(BaseModel):
    """
    数据分支条件
    """
    # 包含的文件 glob 表达式
    includes: List[str] = []
    # 排除的文件 glob 表达式
    excludes: List[str] = []
    # 保存到数据仓库 key
    save_key: str


class SwitchPluginConfig(OutputPluginConfig):
    """
    条件分支上下文插件配置
    """
    # 分支条件
    cases: List[Case] = []
    # 未匹配到分支条件时key
    default_key: Optional[str] = None


class SwitchPlugin(Plugin[SwitchPluginConfig]):
    """
    条件分支上下文插件

    作用: 依据条件对当前上下文数据分组, 并保存到新上下文
    """
    name: str = "switch"

    def execute(self):
        context = self.load_context()

        matched_file_datas = []

        for ca in self.config.cases:
            case_file_datas = paths_includes(context.file_datas, ca.includes)
            case_file_datas = paths_excludes(case_file_datas, ca.excludes)
            matched_file_datas += case_file_datas
            self.save_context(
                Context(file_datas=case_file_datas), ca.save_key)

        if self.config.default_key is not None:
            default_file_datas = []
            for file_data in context.file_datas:
                if file_data not in matched_file_datas:
                    default_file_datas.append(file_data)
            self.save_context(
                Context(file_datas=default_file_datas), self.config.default_key)
