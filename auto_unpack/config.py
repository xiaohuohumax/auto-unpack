from pathlib import Path
from typing import Literal, Optional, Type, TypeVar

from pydantic import BaseModel, Field

from auto_unpack.util.file import read_yaml_file

LogLevelType = Literal[
    "critical", "fatal", "error", "warn", "warning", "info", "debug", "notset"
]


class LoggingConfig(BaseModel):
    """
    日志配置
    """

    # 日志级别
    level: Optional[LogLevelType] = Field(
        default=None, description="日志级别(null: 使用日志配置文件的配置, 默认: null)"
    )
    # 日志配置文件路径
    config_path: Path = Field(
        default_factory=lambda: Path("config/logging.yaml"),
        description="日志配置文件路径(默认: config/logging.yaml)",
    )


class BannerConfig(BaseModel):
    """
    banner配置
    """

    # 是否启用banner
    enabled: bool = Field(default=True, description="是否启用banner")
    # banner文件路径
    file_path: Path = Field(
        default_factory=lambda: Path("banner.txt"),
        description="banner文件路径(默认: banner.txt)",
    )
    # 欢迎信息
    welcome: str = Field(
        default="welcome to use auto-unpack!",
        description="欢迎信息(默认: welcome to use auto-unpack!)",
    )


class AppConfig(BaseModel):
    """
    应用配置
    """

    # 应用名称
    name: str = Field(default="auto-unpack", description="应用名称(默认: auto-unpack)")
    # 信息输出目录
    info_dir: Path = Field(
        default_factory=lambda: Path("info"), description="信息输出目录(默认: info)"
    )
    # 执行前是否清空信息输出目录
    clear_info_dir: bool = Field(
        default=False, description="执行前是否清空信息输出目录(默认: false)"
    )
    # 自定义插件路径
    plugins_dir: Optional[Path] = Field(
        default=None, description="自定义插件路径(默认: null)"
    )


class ProjectConfig(BaseModel):
    """
    项目配置信息
    """

    # 应用配置
    app: AppConfig = Field(default=AppConfig(), description="应用配置")
    # 日志配置
    logging: LoggingConfig = Field(default=LoggingConfig(), description="日志配置")
    # banner配置
    banner: BannerConfig = Field(default=BannerConfig(), description="banner配置")


_T = TypeVar("_T", bound=BaseModel)


def _merge_config(base: dict, add: dict) -> dict:
    """
    合并配置

    合并规则：
    1. 若新增配置中某个 key 对应的值为 dict，则递归合并
    2. 否则，直接覆盖

    :param base: 基础配置
    :param add: 新增配置
    :return: 合并后的配置
    """
    for key, value in add.items():
        if isinstance(value, dict):
            if key not in base:
                base[key] = {}
            _merge_config(base[key], value)
        else:
            base[key] = value


def load_config(config_class: Type[_T], config_dir: Path, mode: str) -> _T:
    """
    加载配置

    加载顺序：
    1. 读取 application.yaml
    2. 读取 application.{mode}.yaml
    3. 合并配置

    合并规则：
    1. 若新增配置中某个 key 对应的值为 dict，则递归合并
    2. 否则，直接覆盖

    :param config_class: 配置类
    :param config_path: 配置文件存放路径
    :param mode: 运行模式
    :return: 配置类实例
    """

    files = [
        Path(config_dir, "application.yaml"),
        Path(config_dir, f"application.{mode}.yaml"),
    ]

    config = {}

    for file in files:
        if not file.exists():
            continue

        new_config = read_yaml_file(file)

        if not isinstance(new_config, dict):
            continue

        _merge_config(config, new_config)

    return config_class.model_validate(config)
