from pathlib import Path
from typing import Literal, Optional, Type, TypeVar

from pydantic import BaseModel, Field

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
    level: Optional[LogLevelType] = Field(
        default=None,
        description="日志级别(null: 使用日志配置文件的配置, 默认: null)"
    )
    # 日志配置文件路径
    config_path: Path = Field(
        default_factory=lambda: Path("config/logging.yaml"),
        description="日志配置文件路径(默认: config/logging.yaml)"
    )


class BannerConfig(BaseModel):
    """
    banner配置
    """
    # 是否启用banner
    enabled: bool = Field(
        default=True,
        description="是否启用banner"
    )
    # banner文件路径
    file_path: Path = Field(
        default_factory=lambda: Path("banner.txt"),
        description="banner文件路径(默认: banner.txt)"
    )
    # 欢迎信息
    welcome: str = Field(
        default="welcome to use auto-unpack!",
        description="欢迎信息(默认: welcome to use auto-unpack!)"
    )


class AppConfig(BaseModel):
    """
    应用配置
    """
    # 应用名称
    name: str = Field(
        default="auto-unpack",
        description="应用名称(默认: auto-unpack)"
    )
    # 信息输出目录
    info_dir: Path = Field(
        default_factory=lambda: Path("info"),
        description="信息输出目录(默认: info)"
    )
    # 执行前是否清空信息输出目录
    clear_info_dir: bool = Field(
        default=False,
        description="执行前是否清空信息输出目录(默认: false)"
    )
    # 自定义插件路径
    plugins_dir: Optional[Path] = Field(
        default=None,
        description="自定义插件路径(默认: null)"
    )


class ProjectConfig(BaseModel):
    """
    项目配置信息
    """
    # 应用配置
    app: AppConfig = Field(
        default=AppConfig(),
        description="应用配置"
    )
    # 日志配置
    logging: LoggingConfig = Field(
        default=LoggingConfig(),
        description="日志配置"
    )
    # banner配置
    banner: BannerConfig = Field(
        default=BannerConfig(),
        description="banner配置"
    )


_T = TypeVar('_T', bound=BaseModel)


def load_config_by_class(config_class: Type[_T], config_dir: Path, mode: str) -> _T:
    """
    加载项目配置

    :param config_class: 配置类
    :param config_dir: 配置目录
    :param mode: 运行模式
    :return: 配置实例
    """
    return load_config(config_class, config_dir, mode)
