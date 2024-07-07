import importlib.util
import inspect
import logging
import os
from pathlib import Path
from typing import Any, Generic, List, Optional, Tuple, TypeVar

from pydantic import BaseModel, ConfigDict

from .store import Context, DataStore, context_default_key

logger = logging.getLogger(__name__)


class PluginConfig(BaseModel):
    """
    插件配置基类
    """
    # 忽略多余参数
    _config = ConfigDict(extra='ignore')


class InputPluginConfig(PluginConfig):
    """
    入口类型插件配置，用作加载数据
    """
    # 上下文保存 key
    save_key: str = context_default_key


class OutputPluginConfig(PluginConfig):
    """
    出口类型插件配置，用作数据最终处理
    """
    # 上下文加载 key
    load_key: str = context_default_key


class HandlePluginConfig(InputPluginConfig, OutputPluginConfig):
    """
    处理类型插件配置，用作数据中间加工
    """
    pass


C = TypeVar('C', bound=PluginConfig)


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
    name: str = ''
    # 插件配置
    config: C
    # 数据仓库
    store: DataStore
    # 插件全局配置
    global_config: PluginGlobalConfig

    def __init__(self, config: C, store: DataStore, global_config: PluginGlobalConfig):
        self.config = config
        self.store = store
        self.global_config = global_config
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
    # todo: 自定义插件目录
    # 插件路径
    plugins_dir = Path(__file__).parent / 'plugin'
    # 插件列表
    plugins: List[Tuple[PluginConfig, Plugin]] = []
    # 是否加载过插件
    is_loaded = False

    def reload_plugins(self):
        """
        重新加载插件
        """
        self.is_loaded = False
        self.plugins = []
        self.load_plugins()

    def load_plugin(self, file_path: Path) -> Optional[Tuple[PluginConfig, Plugin]]:
        """
        加载插件

        :param file_path: 插件文件路径
        """
        suffix = file_path.suffix
        if suffix != '.py':
            return None

        plugin_name = file_path.stem
        spec = importlib.util.spec_from_file_location(
            plugin_name, file_path
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        config_class: PluginConfig = None
        plugin_class: Plugin = None

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
            return (config_class, plugin_class)
        else:
            logger.warning(
                f"Plugin file {plugin_name} has no config or plugin class")

        return None

    def load_plugins(self):
        """
        加载插件
        """
        if self.is_loaded:
            return

        for root, _, files in os.walk(self.plugins_dir):
            for file in files:
                plugin = self.load_plugin(Path(root)/file)
                if plugin is not None:
                    self.plugins.append(plugin)

        logger.info(f"Plugins loaded: {len(self.plugins)}")
        self.is_loaded = True

    def create_plugin(self, config: Any, store: DataStore, global_config: PluginGlobalConfig) -> Plugin:
        """
        根据配置创建插件

        :param config: 插件配置
        :param store: 数据仓库
        :return: 插件实例
        """
        if not self.is_loaded:
            self.load_plugins()

        for config_class, plugin_class in self.plugins:
            if plugin_class.name == dict(config).get('name', None):
                try:
                    config_instance = config_class(**config)
                    return plugin_class(
                        config=config_instance,
                        store=store,
                        global_config=global_config
                    )
                except Exception as e:
                    logger.error(
                        f"Creating flow step `{config.get('name')}` failed: {e}")
                    raise e

        raise ValueError(f"Plugin `{config.get('name')}` not found")


pluginManager = PluginManager()
