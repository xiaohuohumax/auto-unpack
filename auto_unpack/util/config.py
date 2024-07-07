from pathlib import Path
from typing import Type, TypeVar

from pydantic import BaseModel

from .file import read_yaml_file

_T = TypeVar('_T', bound=BaseModel)


def _merge_config(base: dict, add: dict) -> dict:
    """
    合并配置

    合并规则：
    1. 若新增配置中某个 key 对应的值为 dict，则递归合并
    2. 否则，直接覆盖

    :param base: 基础配置
    :param add: 新增配置
    :return: 合并后的配置
    """
    for key, value in add.items():
        if isinstance(value, dict):
            if key not in base:
                base[key] = {}
            _merge_config(base[key], value)
        else:
            base[key] = value


def load_config(config_class: Type[_T], config_dir: Path, mode: str) -> _T:
    """
    加载配置

    加载顺序：
    1. 读取 application.yaml
    2. 读取 application.{mode}.yaml
    3. 合并配置

    合并规则：
    1. 若新增配置中某个 key 对应的值为 dict，则递归合并
    2. 否则，直接覆盖

    :param config_class: 配置类
    :param config_path: 配置文件存放路径
    :param mode: 运行模式
    :return: 配置类实例
    """

    files = [
        Path(config_dir, 'application.yaml'),
        Path(config_dir, f'application.{mode}.yaml'),
    ]

    config = {}

    for file in files:
        if not file.exists():
            continue

        new_config = read_yaml_file(file)

        if not isinstance(new_config, dict):
            continue

        _merge_config(config, new_config)

    return config_class.model_validate(config)
