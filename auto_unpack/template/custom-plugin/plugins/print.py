import logging
from typing import Literal

from pydantic import Field

from auto_unpack.plugin import Plugin, PluginConfig

logger = logging.getLogger(__name__)


class PrintPluginConfig(PluginConfig):
    """
    打印插件配置
    """
    name: Literal["print"] = Field(
        default="print",
        description="打印插件"
    )
    message: str = Field(
        default="Hello, world!",
        description="打印的消息"
    )


class PrintPlugin(Plugin[PrintPluginConfig]):
    """
    打印插件
    """
    name: str = "print"

    def init(self):
        """
        初始化打印插件
        """
        logger.debug("init print plugin")

    def execute(self):
        """
        执行打印插件
        """
        logger.info(self.config.message)
