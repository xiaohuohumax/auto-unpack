import logging
from typing import Literal

from pydantic import Field

from auto_unpack.plugin import Plugin, PluginConfig

logger = logging.getLogger(__name__)


class TemplatePluginConfig(PluginConfig):
    """
    插件模板配置
    """

    name: Literal["_template"] = Field(default="_template", description="插件模板")


class TemplatePlugin(Plugin[TemplatePluginConfig]):
    """
    插件模板
    """

    name: str = "_template"

    def execute(self):
        pass
