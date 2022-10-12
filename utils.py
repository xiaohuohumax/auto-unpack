import json
import os
from datetime import datetime
from pathlib import Path


def abs_path(rel_path: str) -> str:
    return str(Path(Path(__file__).parent, rel_path))


def read_file(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def remove_file(file_path: str) -> None:
    os.remove(file_path)


def write_file(file_path: str, data: str) -> None:
    with open(file_path, 'w+', encoding='utf-8') as f:
        f.write(data)


def exists_file(file_path: str) -> bool:
    return os.path.exists(file_path)


def str_rep(data: str, rep: int = 100) -> str:
    return data * rep


def title_format(title: str, rep: int = 100, rep_str='=', *data: [str]) -> str:
    return '\n'.join([
        str_rep(rep_str, rep),
        f'[{title}]',
        str_rep(rep_str, rep),
        *data
    ])


def path_join(*path) -> str:
    return str(Path(*path))


def dict_format_str(data: dict) -> str:
    return json.dumps(data, indent=4, ensure_ascii=False)


def time_format(time: datetime, format_str: str = '%Y-%m-%d %H:%M:%S.%f') -> str:
    return time.strftime(format_str)


def time_diff(start_time: datetime, end_time: datetime) -> int:
    return (end_time - start_time).seconds
