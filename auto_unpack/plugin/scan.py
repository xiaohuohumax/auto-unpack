import logging
from pathlib import Path
from typing import List

from auto_unpack.plugin import InputPluginConfig, Plugin
from auto_unpack.store import Context, FileData, paths_excludes

logger = logging.getLogger(__name__)


class ScanPluginConfig(InputPluginConfig):
    """
    扫描文件插件配置
    """
    # 扫描目录
    dir: Path
    # 包含的文件类型 glob 语法
    includes: List[str] = ["**/*"]
    # 排除的文件类型 glob 语法
    excludes: List[str] = []
    # 是否包含文件夹
    include_dir: bool = False


class ScanPlugin(Plugin[ScanPluginConfig]):
    """
    扫描文件插件

    作用: 扫描指定目录下的文件, 并保存到指定的数据仓库中
    """
    name: str = "scan"

    def execute(self):
        file_datas: List[FileData] = []

        for include in self.config.includes:
            for f in self.config.dir.rglob(include):
                if not self.config.include_dir and not f.is_file():
                    continue
                file_data = FileData(path=f, search_path=self.config.dir)
                file_datas.append(file_data)

        file_datas = paths_excludes(file_datas, self.config.excludes)

        logger.info(f"Found {len(file_datas)} files")

        self.save_context(Context(file_datas=file_datas))
