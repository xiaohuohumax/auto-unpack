import logging
from pathlib import Path
from typing import Any, List, Literal, Optional

from pydantic import Field, field_validator

from auto_unpack.plugin import Plugin, PluginConfig
from auto_unpack.util.file import get_next_not_exist_path

logger = logging.getLogger(__name__)


class FlatPluginConfig(PluginConfig):
    """
    扁平化文件夹插件配置
    """

    name: Literal["flat"] = Field(default="flat", description="扁平化文件夹插件")
    dir: Path = Field(description="需要扁平化的文件夹")
    depth: Optional[int] = Field(
        default=None,
        description="扁平化的深度(null: 不限制深度, 默认: null)",
        json_schema_extra={"minimum": 1},
    )

    @field_validator("depth")
    @classmethod
    def validate_depth(cls, v: Any):
        if v is not None and v < 1:
            raise ValueError("depth must be greater than or equal to 1")
        return v


class FlatPlugin(Plugin[FlatPluginConfig]):
    """
    扁平化文件夹插件

    作用: 将目标文件夹下的所有文件扁平化到目标文件夹根目录下

    例如:

    ```txt
    dir/
        file1.txt
        subdir/
            file2.txt

    ```
    扁平化后:
    ```txt
    dir/
        file1.txt
        file2.txt
    ```
    """

    name: str = "flat"

    def _depth_filter(self, path: Path, now_depth: int = 0) -> List[Path]:
        child = list(path.iterdir())
        if self.config.depth is not None and now_depth >= self.config.depth:
            # 超过深度则不再遍历
            return child

        res = []
        for file in child:
            if file.is_dir():
                res += self._depth_filter(file, now_depth + 1)
            elif file.is_file() and now_depth != 0:
                # 排除本身就在根目录的文件情况
                res.append(file)
        return res

    def execute(self):
        if not self.config.dir.exists():
            raise FileNotFoundError(f"Directory {self.config.dir} not found")

        files = self._depth_filter(self.config.dir)

        for file in files:
            target_file = get_next_not_exist_path(self.config.dir.joinpath(file.name))
            file.rename(target_file)

        logger.info(f"Flat success, {len(files)} files flattened")
