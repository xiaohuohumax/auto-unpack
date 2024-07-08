from pathlib import Path
from typing import Literal, Optional, Type, TypeVar

from pydantic import BaseModel

from .env import env
from .util.config import load_config

LogLevelType = Literal[
    'critical', 'fatal', 'error',
    'warn', 'warning', 'info',
    'debug', 'notset'
]


class LoggingConfig(BaseModel):
    """
    日志配置
    """
    # 日志级别
    level: Optional[LogLevelType] = None
    # 日志配置文件路径
    config_path: Path = Path("config/logging.yaml")


class BannerConfig(BaseModel):
    """
    banner配置
    """
    # 是否启用banner
    enabled: bool = True
    # banner文件路径
    file_path: Path = Path("banner.txt")
    # 欢迎信息
    welcome: str = ""


class AppConfig(BaseModel):
    """
    应用配置
    """
    # 应用名称
    name: str = ""
    # 信息输出目录
    info_dir: Path = Path("info")
    # 执行前是否清空信息输出目录
    clear_info_dir: bool = False


class ProjectConfig(BaseModel):
    """
    项目配置信息
    """
    # 应用配置
    app: AppConfig = AppConfig()
    # 日志配置
    logging: LoggingConfig = LoggingConfig()
    # banner
    banner: BannerConfig = BannerConfig()


_T = TypeVar('_T', bound=BaseModel)


def load_config_by_class(config_class: Type[_T]) -> _T:
    """
    加载项目配置

    :param config_class: 配置类
    :return: 配置实例
    """
    return load_config(config_class, env.config_dir, env.mode)


# 配置
config = load_config_by_class(ProjectConfig)
