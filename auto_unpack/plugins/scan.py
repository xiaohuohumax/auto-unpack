import logging
from pathlib import Path
from typing import List, Literal

from pydantic import Field

from auto_unpack.plugin import InputPluginConfig, Plugin
from auto_unpack.store import Context, FileData, paths_excludes

logger = logging.getLogger(__name__)


class ScanPluginConfig(InputPluginConfig):
    """
    扫描文件插件配置
    """

    name: Literal["scan"] = Field(default="scan", description="扫描文件插件")
    dir: Path = Field(description="扫描目录")
    includes: List[str] = Field(
        default=["**/*"], description="包含的文件路径列表(glob 语法, 默认: [**/*])"
    )
    excludes: List[str] = Field(
        default=[], description="排除的文件路径列表(glob 语法, 默认: [])"
    )
    include_dir: bool = Field(default=False, description="是否包含文件夹(默认: false)")
    deep: bool = Field(default=True, description="是否递归扫描子目录(默认: true)")


class ScanPlugin(Plugin[ScanPluginConfig]):
    """
    扫描文件插件

    作用: 扫描指定目录下的文件, 并保存到指定的数据仓库中
    """

    name: str = "scan"

    def execute(self):
        file_datas: List[FileData] = []

        glob_func = self.config.dir.rglob if self.config.deep else self.config.dir.glob
        for include in self.config.includes:
            for f in glob_func(include):
                if not self.config.include_dir and not f.is_file():
                    continue
                file_data = FileData(path=f, search_path=self.config.dir)
                file_datas.append(file_data)

        file_datas = paths_excludes(file_datas, self.config.excludes)

        logger.info(f"Found {len(file_datas)} files")

        self.save_context(Context(file_datas=file_datas))
