import logging
from typing import List, Optional

from auto_unpack.plugin import HandlePluginConfig, Plugin
from auto_unpack.store import Context, paths_excludes, paths_includes

logger = logging.getLogger(__name__)


class FilterPluginConfig(HandlePluginConfig):
    """
    过滤插件配置
    """
    # 包含的文件 glob 表达式
    includes: List[str] = ["**/*"]
    # 排除的文件 glob 表达式
    excludes: List[str] = []
    # 排除掉的上下文 key
    exclude_key: Optional[str] = None
    # todo: 增加各种筛选条件, 比如文件大小限制


class FilterPlugin(Plugin[FilterPluginConfig]):
    """
    过滤插件

    作用: 过滤文件数据, 保留符合条件的文件数据
    """
    name: str = "filter"

    def execute(self):
        context = self.load_context()

        include_file_datas = paths_includes(
            context.file_datas, self.config.includes)
        include_file_datas = paths_excludes(
            include_file_datas, self.config.excludes)

        self.save_context(Context(file_datas=include_file_datas))

        logger.info(f"Matched {len(include_file_datas)} files.")

        if self.config.exclude_key is not None:
            exclude_file_datas = [
                f for f in context.file_datas if f not in include_file_datas]
            self.save_context(
                Context(file_datas=exclude_file_datas), self.config.exclude_key)
