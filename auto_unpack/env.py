from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

from .args import args

load_dotenv(override=True)


class Env(BaseSettings, case_sensitive=False):
    """
    环境变量 (忽略大小写)
    """

    # 环境模式
    mode: str = 'dev'

    # 配置文件存放目录
    config_dir: Path = Path('config')


# 环境变量
env = Env()


if args.mode is not None:
    env.mode = args.mode
