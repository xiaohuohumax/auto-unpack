import logging

from auto_unpack.plugin import Plugin, PluginConfig

logger = logging.getLogger(__name__)


class TemplatePluginConfig(PluginConfig):
    """
    插件模板配置
    """
    pass


class TemplatePlugin(Plugin[TemplatePluginConfig]):
    """
    插件模板
    """
    name: str = "_template"

    def execute(self):
        pass
