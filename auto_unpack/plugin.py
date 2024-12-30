import importlib.util
import inspect
import logging
import os
from pathlib import Path
from typing import Any, Generic, List, Optional, Tuple, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from . import constant
from .store import Context, DataStore

logger = logging.getLogger(__name__)


class PluginConfig(BaseModel):
    """
    插件配置基类
    """

    # 忽略多余参数
    model_config = ConfigDict(extra="ignore")
    # 插件名称
    name: str = ""


class InputPluginConfig(PluginConfig):
    """
    入口类型插件配置，用作加载数据
    """

    # 上下文保存 key
    save_key: str = Field(
        default=constant.CONTEXT_DEFAULT_KEY, description="上下文保存 key"
    )


class OutputPluginConfig(PluginConfig):
    """
    出口类型插件配置，用作数据最终处理
    """

    # 上下文加载 key
    load_key: str = Field(constant.CONTEXT_DEFAULT_KEY, description="上下文加载 key")


class HandlePluginConfig(InputPluginConfig, OutputPluginConfig):
    """
    处理类型插件配置，用作数据中间加工
    """

    pass


C = TypeVar("C", bound=PluginConfig)


class PluginGlobalConfig(BaseModel):
    """
    插件全局配置元类
    """

    # 信息输出目录
    info_dir: Path


class Plugin(Generic[C]):
    """
    插件基类
    """

    # 插件名称(唯一标识)
    name: str = ""
    # 插件配置
    config: C
    # 数据仓库
    store: DataStore
    # 插件全局配置
    global_config: PluginGlobalConfig
    # 插件管理器
    plugin_manager: "PluginManager"

    def __init__(
        self,
        config: C,
        store: DataStore,
        global_config: PluginGlobalConfig,
        plugin_manager: "PluginManager",
    ):
        self.config = config
        self.store = store
        self.global_config = global_config
        self.plugin_manager = plugin_manager
        self.init()

    def init(self):
        """
        插件初始化
        """
        pass

    def load_context(self, context_key: Optional[str] = None) -> Context:
        """
        加载上下文

        :param context_key: 上下文保存 key
        :return: 上下文
        """
        if context_key is None and isinstance(self.config, OutputPluginConfig):
            context_key = self.config.load_key
        return self.store.load_context(context_key)

    def save_context(self, context: Context, context_key: Optional[str] = None):
        """
        保存上下文

        :param context: 上下文
        :param context_key: 上下文保存 key
        """
        if context_key is None and isinstance(self.config, InputPluginConfig):
            context_key = self.config.save_key
        self.store.save_context(context_key, context)

    def execute(self):
        """
        插件执行逻辑
        """
        pass


class PluginManager:
    """
    插件管理器
    """

    # 插件列表
    plugins: List[Tuple[PluginConfig, Plugin]] = []

    def _save_plugin(self, config: PluginConfig, plugin: Plugin):
        """
        保存插件, 同名则覆盖(name)

        :param config: 插件配置
        :param plugin: 插件
        """
        index = next(
            (i for i, (_, p) in enumerate(self.plugins) if p.name == plugin.name), -1
        )
        if index != -1:
            logger.warning(f"Plugin `{plugin.name}` already exists, replaced")
            self.plugins[index] = (config, plugin)
        else:
            self.plugins.append((config, plugin))

    def _load_plugin_by_file(
        self, file_path: Path
    ) -> Optional[Tuple[PluginConfig, Plugin]]:
        """
        通过文件加载插件

        :param file_path: 插件文件路径
        """
        suffix = file_path.suffix
        if suffix != ".py":
            return None

        plugin_name = file_path.stem
        spec = importlib.util.spec_from_file_location(plugin_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        config_class: Optional[PluginConfig] = None
        plugin_class: Optional[Plugin] = None

        for _, module_class in inspect.getmembers(module, inspect.isclass):
            if module_class.__module__ != module.__name__:
                # 排除导入的模块
                continue
            if issubclass(module_class, Plugin) and module_class != Plugin:
                plugin_class = module_class
            if issubclass(module_class, PluginConfig) and module_class != PluginConfig:
                config_class = module_class

        if config_class is not None and plugin_class is not None:
            logger.debug(f"Plugin `{plugin_class.name}` loaded")
            self._save_plugin(config_class, plugin_class)
        else:
            logger.warning(f"Plugin file {plugin_name} has no config or plugin class")

    def load_plugin(self, plugin_path: Path):
        """
        加载插件

        :param plugin_path: 插件目录/文件路径
        """
        if not plugin_path.exists():
            logger.warning(f"Plugin path {plugin_path} not found")
            return

        if plugin_path.is_file():
            logger.debug(f"Loading plugin from {plugin_path}")
            self._load_plugin_by_file(plugin_path)
            return

        logger.debug(f"Loading plugins from {plugin_path}")
        for root, _, files in os.walk(plugin_path):
            for file in files:
                if file.startswith("__") or not file.endswith(".py"):
                    continue
                self._load_plugin_by_file(Path(root) / file)

    def load_plugin_by_class(self, config_class: Any, plugin_class: Any):
        """
        通过类加载插件

        :param config_class: 插件配置类
        :param plugin_class: 插件类
        """
        logger.debug(f"Loading plugin by class `{config_class.__name__}`")

        if not issubclass(plugin_class, Plugin):
            logger.warning(
                f"Plugin class `{plugin_class}` is not a subclass of `Plugin`"
            )
            return
        elif not issubclass(config_class, PluginConfig):
            logger.warning(
                f"Plugin config class `{config_class}` is not a subclass of `PluginConfig`"
            )
            return

        logger.debug(f"Plugin `{plugin_class.name}` loaded")
        self._save_plugin(config_class, plugin_class)

    def create_plugin_instance(
        self, config: Any, store: DataStore, global_config: PluginGlobalConfig
    ) -> Plugin:
        """
        根据配置创建插件实例

        :param config: 插件配置
        :param store: 数据仓库
        :return: 插件实例
        """
        for config_class, plugin_class in self.plugins:
            if plugin_class.name == dict(config).get("name", None):
                try:
                    config_instance = config_class(**config)
                    return plugin_class(
                        config=config_instance,
                        store=store,
                        global_config=global_config,
                        plugin_manager=self,
                    )
                except Exception as e:
                    logger.error(
                        f"Creating flow step `{config.get('name')}` failed: {e}"
                    )
                    raise e

        raise ValueError(f"Plugin `{config.get('name')}` not found")
