import argparse
from typing import Optional

from pydantic import BaseModel


class Args(BaseModel):
    """
    命令行参数
    """
    # 模式
    mode: Optional[str] = None


parser = argparse.ArgumentParser(description="")
parser.add_argument('-m', '--mode', dest='mode', type=str,
                    default=None, help='运行模式')


def load_args() -> Args:
    """
    加载命令行参数

    :return: 命令行参数
    """
    return Args.model_validate(vars(parser.parse_args()))
