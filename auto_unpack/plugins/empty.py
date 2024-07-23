import logging
from pathlib import Path

from auto_unpack.plugin import Plugin, PluginConfig
from auto_unpack.util.file import clean_empty_dir

logger = logging.getLogger(__name__)


class EmptyPluginConfig(PluginConfig):
    """
    空文件夹清理插件配置
    """
    # 要清理的目录
    dir: Path


class EmptyPlugin(Plugin[EmptyPluginConfig]):
    """
    空文件夹清理插件

    作用: 清理文件夹下所有空文件夹
    """
    name: str = "empty"

    def execute(self):
        if not self.config.dir.exists():
            logger.warning(f"Folder {self.config.dir} not exists, skip.")
        clean_empty_dir(self.config.dir)
