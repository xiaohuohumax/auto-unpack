import subprocess
from typing import List


def run_cmd(cmd: List[str]) -> (int, str):
    """
    调用命令行 适配中文忽略异常
    :param cmd: 命令
    :return: 状态码,返回信息
    """
    with subprocess.Popen(' '.join(cmd), stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          shell=True) as proc:
        info, _ = proc.communicate()
        return proc.returncode, info.decode('utf-8', errors='ignore')


def bool_map(flag: bool, flag_map: (str, str) = ('是', '否')) -> str:
    return flag_map[0 if flag else 1]
