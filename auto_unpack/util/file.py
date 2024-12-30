import os
from pathlib import Path
from typing import Any, List

from ruamel.yaml import YAML


def read_file(file_path: Path) -> str:
    """
    读取文件内容

    :param file_path: 文件路径
    :param encoding: 编码格式默认utf8
    :return: 文件内容
    """
    with open(file_path, encoding="utf8") as f:
        return f.read()


def write_file(file_path: Path, content: str):
    """
    写入文件内容

    :param file_path: 文件路径
    :param content: 文件内容
    :return: None
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf8") as f:
        f.write(content)


def read_file_lines(file_path: Path) -> List[str]:
    """
    读取文件行

    :param file_path: 文件路径
    :return: 文件行列表
    """
    return read_file(file_path).splitlines()


def read_yaml_file(file_path: Path) -> Any:
    """
    读取yaml文件

    :param file_path: 文件路径
    :param encoding: 编码格式默认utf8
    :return: yaml文件内容
    """
    return YAML(typ="safe").load(read_file(file_path))


def get_next_not_exist_path(path: Path) -> Path:
    """
    获取下一个不存在的路径

    test => test(1) => test(2)

    :param dir_path: 路径
    :return: 下一个不存在的路径
    """
    index = 1
    new_path = path
    while new_path.exists():
        if new_path.is_dir():
            name = f"{path.name}({index})"
        else:
            name = f"{path.stem}({index}){path.suffix}"
        new_path = path.with_name(name)
        index += 1
    return new_path


def path_equal(path1: Path, path2: Path) -> bool:
    """
    判断两个路径是否相等

    :param path1: 路径1
    :param path2: 路径2
    :return: 路径是否相等
    """
    return str(path1.resolve()) == str(path2.resolve())


def rename_file(old_file: Path, new_file: Path) -> bool:
    """
    文件重命名

    :param old_file: 老文件路径
    :param new_file: 新文件路径
    :return: 是否重命名
    """
    if path_equal(old_file, new_file):
        return False
    old_file.rename(new_file)
    return True


def is_path_in_includes(path: Path, includes: List[Path]) -> bool:
    """
    判断文件是否在includes列表中

    :param path: 文件路径
    :param includes: includes列表
    :return: 是否在includes列表中
    """
    return str(path.resolve()) in [str(include.resolve()) for include in includes]


def clean_empty_dir(dir_path: Path):
    """
    清理文件夹下所有空目录

    :param dir_path: 目录路径
    :return: None
    """
    if not dir_path.is_dir() or not dir_path.exists():
        return

    for child in os.listdir(dir_path):
        path = dir_path / child

        if not path.is_dir():
            continue

        clean_empty_dir(path)

        if len(os.listdir(path)) == 0:
            path.rmdir()
