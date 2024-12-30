import logging
from pathlib import Path
from typing import Literal

from pydantic import Field

from auto_unpack.plugin import Plugin, PluginConfig
from auto_unpack.util.file import clean_empty_dir

logger = logging.getLogger(__name__)


class EmptyPluginConfig(PluginConfig):
    """
    空文件夹清理插件配置
    """

    name: Literal["empty"] = Field(default="empty", description="空文件夹清理插件")
    dir: Path = Field(description="需要清理空文件夹的目录")


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
