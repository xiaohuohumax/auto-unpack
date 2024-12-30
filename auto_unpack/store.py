import fnmatch
import logging
from pathlib import Path
from typing import Dict, List

from pydantic import BaseModel

from . import constant

logger = logging.getLogger(__name__)


class FileData(BaseModel):
    """
    文件数据类
    """

    # 文件路径
    path: Path
    # 搜索路径
    search_path: Path

    @property
    def relative_path(self) -> Path:
        """
        获取相对于搜索路径的相对路径
        """
        return self.path.relative_to(self.search_path)

    def __hash__(self):
        return hash((str(self.path), str(self.search_path)))

    def __eq__(self, other):
        return (
            isinstance(other, FileData)
            and self.path == other.path
            and self.search_path == other.search_path
        )


def path_glob_match(path: Path, pattern: str) -> bool:
    """
    判断路径是否匹配模式

    :param path: 路径
    :param pattern: glob 规则
    :return: 是否匹配
    """
    try:
        path_str = str(path).replace("\\", "/")
        if not path_str.endswith("/") and path.is_dir():
            path_str += "/"
        return fnmatch.fnmatchcase(path_str, pattern)
    except Exception:
        # 当文件不存在时，回退至使用 match 方法
        # 缺点无法区分是文件还是目录
        # 例如:
        # Path('a').match('*/') => True
        # Path('a/').match('*/') => True
        logger.warning(
            f"Failed to use fnmatch.fnmatchcase to match path `{path}` with pattern `{pattern}`"
        )
        return path.match(pattern)


def paths_includes(file_datas: List[FileData], includes: List[str]) -> List[FileData]:
    """
    筛选路径

    :param file_datas: 文件数据列表
    :param includes: 包含规则
    :return: 筛选后的路径列表
    """
    res_paths = []

    for file_data in file_datas:
        for include in includes:
            if path_glob_match(file_data.path, include):
                res_paths.append(file_data)
                break

    return res_paths


def paths_excludes(file_datas: List[FileData], excludes: List[str]) -> List[FileData]:
    """
    筛选路径

    :param file_datas: 文件数据列表
    :param excludes: 排除规则
    :return: 筛选后的路径列表
    """
    res_paths = []
    for file_data in file_datas:
        for exclude in excludes:
            if path_glob_match(file_data.path, exclude):
                break
        else:
            res_paths.append(file_data)

    return res_paths


class Context(BaseModel):
    """
    上下文类
    """

    # 文件数据列表
    file_datas: List[FileData] = []


class DataStore:
    """
    数据存储类
    """

    contexts: Dict[str, Context] = {}

    def __init__(self):
        self.empty_all_context()
        self.save_context(constant.CONTEXT_DEFAULT_KEY, Context())

    def load_context(self, context_key) -> Context:
        """
        加载上下文
        """
        if context_key not in self.contexts:
            raise KeyError(f"Context key `{context_key}` not found in data store")
        return self.contexts[context_key]

    def save_context(self, context_key, context: Context):
        """
        保存上下文
        """
        # 数据深拷贝防止上下文数据异常
        self.contexts[context_key] = context.model_copy()

    def empty_all_context(self):
        """
        清空所有上下文
        """
        self.contexts = {}
