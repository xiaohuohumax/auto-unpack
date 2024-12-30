import logging
import shutil
from typing import Literal

from pydantic import Field

from auto_unpack.plugin import OutputPluginConfig, Plugin
from auto_unpack.store import Context

logger = logging.getLogger(__name__)


class RemovePluginConfig(OutputPluginConfig):
    """
    删除文件插件配置
    """

    name: Literal["remove"] = Field(default="remove", description="删除文件插件")


class RemovePlugin(Plugin[RemovePluginConfig]):
    """
    删除文件插件

    作用: 删除数据仓库中的指定文件
    """

    name: str = "remove"

    def execute(self):
        context = self.load_context()

        for file_data in context.file_datas:
            file = file_data.path
            logger.debug(f"Removing file: {file}")
            if not file.exists():
                continue
            if file.is_file():
                file.unlink()
            elif file.is_dir():
                shutil.rmtree(file)

        self.save_context(Context(file_datas=[]), self.config.load_key)
