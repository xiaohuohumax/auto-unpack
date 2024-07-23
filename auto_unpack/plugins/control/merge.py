import logging
from typing import List, Set

from auto_unpack.plugin import InputPluginConfig, Plugin
from auto_unpack.store import Context, FileData

logger = logging.getLogger(__name__)


class MergePluginConfig(InputPluginConfig):
    """
    合并上下文插件配置
    """
    context_keys: List[str] = []


class MergePlugin(Plugin[MergePluginConfig]):
    """
    合并上下文插件

    作用：将多个上下文数据合并到一个上下文数据中
    """
    name: str = "merge"

    def execute(self):
        file_datas: Set[FileData] = set()

        for c in [self.load_context(key) for key in self.config.context_keys]:
            for f in c.file_datas:
                file_datas.add(f)

        self.save_context(Context(file_datas=file_datas))
