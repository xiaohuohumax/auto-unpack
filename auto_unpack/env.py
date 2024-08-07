from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv(override=True)


class Env(BaseSettings, case_sensitive=False):
    """
    环境变量 (忽略大小写)
    """

    # 环境模式
    mode: str = 'dev'

    # 配置文件存放目录
    config_dir: Path = Path('config')


def load_env_by_mode(mode: Optional[str] = None) -> Env:
    """
    根据模式加载环境变量

    :param mode: 环境模式
    :return: 环境变量
    """
    env = Env()
    if mode is not None:
        env.mode = mode
    return env
