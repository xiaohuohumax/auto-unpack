import logging
import re
from pathlib import Path
from typing import List, Literal, Union

from pydantic import BaseModel, model_validator
from typing_extensions import Self

from auto_unpack.plugin import HandlePluginConfig, Plugin
from auto_unpack.store import Context, FileData
from auto_unpack.util.file import rename_file

logger = logging.getLogger(__name__)


class Rule(BaseModel):
    """
    改名规则基类
    """

    def rename(self, file: Path) -> Path:
        return file


class ReplaceRule(Rule):
    """
    改名规则：替换
    """
    mode: Literal['replace'] = 'replace'
    # 匹配字符串
    search: str
    # 替换字符串
    replace: str
    # 替换次数，-1 表示全部替换
    count: int = -1

    def rename(self, file: Path) -> Path:
        new_name = file.name.replace(self.search, self.replace, self.count)
        new_file = file.with_name(new_name)
        if rename_file(file, new_file):
            logger.info(f"Rename {file} to {new_file}")
        return new_file


# 正则表达式匹配模式
flag_map = {
    # 只匹配 ASCII 字符。
    'a': re.ASCII,
    # 忽略大小写。
    'i': re.IGNORECASE,
    # 匹配 Unicode 字符。
    'u': re.UNICODE
}

flag_keys = list(flag_map.keys())


class ReRule(Rule):
    """
    改名规则：正则表达式
    """
    mode: Literal['re'] = 're'
    # 正则表达式
    pattern: str
    # 替换字符串
    replace: str
    # 替换次数，0 表示不限次数
    count: int = 0
    # 正则表达式匹配模式
    flags: str = ''

    @model_validator(mode='after')
    def check_flags(self) -> Self:
        flags = self.flags
        for flag in flags:
            if flag not in flag_keys:
                raise ValueError(f"Invalid flag: {flag} not in {flag_keys}")
        return self

    def rename(self, file: Path) -> Path:
        flags = 0
        for flag in self.flags:
            flags |= flag_map[flag]

        new_name = re.sub(self.pattern, self.replace,
                          file.name, count=self.count, flags=flags)
        new_file = file.with_name(new_name)
        if rename_file(file, new_file):
            logger.info(f"Rename {file} to {new_file}")
        return new_file


class RenamePluginConfig(HandlePluginConfig):
    """
    改名插件配置
    """
    # 规则链
    rules: List[Union[ReplaceRule, ReRule]] = []


class RenamePlugin(Plugin[RenamePluginConfig]):
    """
    改名插件

    作用: 按照规则链对数据仓库中的文件进行改名
    """
    name: str = "rename"

    def execute(self):
        context = self.load_context()

        new_file_datas: List[FileData] = []

        for file_data in context.file_datas:
            new_file_data = file_data.model_copy()
            for rule in self.config.rules:
                new_file_data.path = rule.rename(new_file_data.path)
            new_file_datas.append(new_file_data)

        self.save_context(Context(file_datas=new_file_datas))