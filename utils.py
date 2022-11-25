import os
import re
import uuid
from pathlib import Path


def abs_path(rel_path: str) -> str:
    # 获取绝对路径
    return rel_path if os.path.isabs(rel_path) else str(Path(Path(__file__).parent, rel_path))


def path_join(*path) -> str:
    # 路径拼接
    return str(Path(*path))


def read_file(file_path: str) -> str:
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def remove_file(file_path: str) -> None:
    # 删除文件
    os.remove(file_path)


def remove_folder(dir_path: str) -> None:
    # 删除文件件
    os.rmdir(dir_path)


def write_file(file_path: str, data: str) -> None:
    # 写入文件
    with open(file_path, 'w+', encoding='utf-8') as f:
        f.write(data)


def rename_file(fa: str, old_name: str, new_name: str) -> None:
    # 文件改名
    os.rename(path_join(fa, old_name), path_join(fa, new_name))


def is_exists_file(file_path: str) -> bool:
    # 文件是否存在
    return os.path.exists(file_path)


def str_rep(data: str, rep: int = 100) -> str:
    # 字符串重复
    return data * rep


def title_format(title: str, rep: int = 100, rep_str='=', *data: [str]) -> str:
    # 字符串显示 title
    # =======================
    # title
    # =======================
    # data
    return '\n'.join([
        str_rep(rep_str, rep),
        f'[{title}]',
        str_rep(rep_str, rep),
        *data
    ])


def del_empty_folder(clear_path: str) -> (bool, int):
    # 删除空文件夹
    has_file = False
    del_count = 0
    for item in os.listdir(clear_path):
        really_path = os.path.join(clear_path, item)
        if os.path.isfile(really_path):
            # 文件
            has_file = True
        elif os.path.isdir(really_path):
            # 文件夹
            item_has_file, item_del_count = del_empty_folder(really_path)
            del_count += item_del_count
            if not item_has_file:
                # 不存在子文件
                remove_folder(really_path)
                del_count += 1
            else:
                has_file = True
    return has_file, del_count


def bool_map(flag: bool, flag_map: (str, str) = ('是', '否')) -> str:
    # 布尔 映射 [是/否]
    return flag_map[0 if flag else 1]


def is_re_match(pattern: str, string: str) -> bool:
    # 是否存在符合条件的字符串
    return len(re.findall(pattern, string)) > 0


def create_uuid() -> str:
    # 创建 uuid 字符串
    return str(uuid.uuid1().hex)
