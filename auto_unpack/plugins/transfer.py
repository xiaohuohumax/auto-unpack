import logging
import shutil
from pathlib import Path
from typing import List, Literal

from pydantic import Field

from auto_unpack.plugin import HandlePluginConfig, Plugin
from auto_unpack.store import Context, FileData
from auto_unpack.util.file import get_next_not_exist_path, path_equal

logger = logging.getLogger(__name__)


class TransferPluginConfig(HandlePluginConfig):
    """
    转移插件配置
    """

    name: Literal["transfer"] = Field(default="transfer", description="转移插件")
    mode: Literal["move", "copy"] = Field(
        description="转移模式\nmove: 移动\ncopy: 复制"
    )
    target_dir: Path = Field(description="目标路径")
    keep_structure: bool = Field(
        default=True, description="是否保持目录结构(相对于扫描路径, 默认: true)"
    )
    overwrite_mode: Literal["rename", "overwrite", "skip"] = Field(
        default="rename",
        description="覆盖模式(默认: rename)\nrename: 重命名\noverwrite: 覆盖\nskip: 跳过",
    )


class TransferPlugin(Plugin[TransferPluginConfig]):
    """
    转移插件

    作用: 移动或复制文件到指定目录
    """

    name: str = "transfer"

    def execute(self):
        context = self.load_context()

        new_file_datas: List[FileData] = []

        for file in context.file_datas:
            new_file = file.model_copy()

            # 获取新的文件路径
            if self.config.keep_structure:
                target_path = self.config.target_dir / new_file.relative_path
            else:
                target_path = self.config.target_dir / new_file.path.name

            target_path.parent.mkdir(parents=True, exist_ok=True)

            if not path_equal(target_path, new_file.path):
                if target_path.exists():
                    # 处理覆盖模式
                    if self.config.overwrite_mode == "overwrite":
                        target_path.unlink()
                    elif self.config.overwrite_mode == "skip":
                        continue
                    elif self.config.overwrite_mode == "rename":
                        target_path = get_next_not_exist_path(target_path)
                if self.config.mode == "move":
                    new_file.path.rename(target_path)
                elif self.config.mode == "copy":
                    shutil.copy(new_file.path, target_path)

            new_file.path = target_path
            new_file.search_path = self.config.target_dir
            new_file_datas.append(new_file)

        self.save_context(Context(file_datas=new_file_datas))
