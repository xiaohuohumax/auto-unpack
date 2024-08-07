import logging
from typing import Literal

from pydantic import Field

from auto_unpack.plugin import OutputPluginConfig, Plugin
from auto_unpack.util.file import get_next_not_exist_path, write_file

logger = logging.getLogger(__name__)


class LogPluginConfig(OutputPluginConfig):
    """
    日志插件配置
    """
    name: Literal['log'] = Field(
        default='log',
        description="日志插件"
    )
    file_name: str = Field(
        default='log',
        description="日志文件名(默认: log)"
    )


class LogPlugin(Plugin[LogPluginConfig]):
    """
    日志插件

    作用: 上下文信息保存到文件
    """
    name: str = "log"

    def execute(self):
        context = self.load_context()

        log_path = get_next_not_exist_path(
            self.global_config.info_dir / f'{self.config.file_name}.json'
        )

        write_file(log_path, context.model_dump_json(indent=2))

        logger.info(f'Log file data saved to {log_path}')
