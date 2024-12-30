from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

from .args import Args


class Env(BaseSettings, case_sensitive=False):
    """
    环境变量 (忽略大小写)
    """

    # 环境模式
    mode: str = "dev"

    # 配置文件存放目录
    config_dir: Path = Path("config")


def load_env(args: Args) -> Env:
    """
    根据命令行参数加载环境变量

    :param args: 命令行参数
    :return: 环境变量
    """
    load_dotenv(override=True)

    env = Env()
    if args.mode is not None:
        env.mode = args.mode
    if args.config_dir is not None:
        env.config_dir = args.config_dir

    return env
