import logging
import subprocess
from typing import List, Tuple

logger = logging.getLogger(__name__)


def exec_cmd(cmds: List[str], decode: str = "utf-8") -> Tuple[int, str]:
    """
    调用命令行

    :param decode: 编码格式
    :param cmd: 命令
    :return: 状态码，返回信息
    """
    with subprocess.Popen(
        " ".join(cmds),
        stdin=None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    ) as proc:
        info, _ = proc.communicate()
        return proc.returncode, info.decode(decode, errors="ignore")
