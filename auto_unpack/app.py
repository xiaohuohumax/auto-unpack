import logging
import shutil
from pathlib import Path
from typing import Any, List

from pydantic import BaseModel

from . import constant
from .args import Args, load_args
from .config import ProjectConfig, load_config
from .env import Env, load_env
from .plugin import Plugin, PluginGlobalConfig, PluginManager
from .store import DataStore
from .util.file import read_file
from .util.logging import config_logging

logger = logging.getLogger(__name__)


class FlowConfig(BaseModel):
    """
    流程配置
    """

    steps: List[Any] = []


class ProjectFlowConfig(BaseModel):
    """
    项目流程配置
    """

    # 流程配置
    flow: FlowConfig = FlowConfig()


class App:
    # 命令行参数
    args: Args
    # 环境变量
    env: Env
    # 项目配置
    config: ProjectConfig
    # 流程(插件实例)
    flows: List[Plugin] = []
    # 数据仓库(插件间共享数据)
    store: DataStore = DataStore()
    # 插件全局配置
    plugin_global_config: PluginGlobalConfig
    # 插件管理器
    plugin_manager: PluginManager

    def _print_banner(self):
        """
        打印 banner
        """
        if not self.config.banner.enabled:
            return

        if not self.config.banner.file_path.exists():
            return

        print(read_file(self.config.banner.file_path))
        print(self.config.banner.welcome + "\n")

    def _create_flows(self):
        """
        根据配置创建流程
        """
        if len(self.flows) != 0:
            return

        logger.info("Creating flows...")
        flow_config = load_config(ProjectFlowConfig, self.env.config_dir, self.env.mode)

        for step in flow_config.flow.steps:
            plugin = self.plugin_manager.create_plugin_instance(
                step, self.store, self.plugin_global_config
            )
            logger.debug(f"Flow step `{step.get('name')}` created")
            self.flows.append(plugin)

        logger.info(f"Flows created: {len(self.flows)}")

    def _clear_info_dir(self):
        """
        清空 info 目录
        """
        if self.config.app.clear_info_dir:
            info_dir = self.config.app.info_dir
            logger.info("Clearing info dir...")
            if info_dir.exists():
                shutil.rmtree(info_dir, ignore_errors=True)

    def _execute_flows(self):
        """
        执行流程
        """
        logger.info("Executing flows...")
        flows_count = len(self.flows)
        for i, flow in enumerate(self.flows):
            logger.info(f"{i+1}/{flows_count} Executing flow `{flow.name}`")
            logger.debug(f"Config: {flow.config.dict()}")
            flow.execute()

    def __init__(self):
        # 加载配置
        self.args = load_args()
        self.env = load_env(self.args)
        self.config = load_config(
            config_class=ProjectConfig,
            config_dir=self.env.config_dir,
            mode=self.env.mode,
        )
        # 打印 banner
        self._print_banner()
        # 配置日志
        config_logging(self.config.logging.config_path, self.config.logging.level)

        logger.info("Initializing app...")
        self.plugin_manager = PluginManager()
        # 加载内置插件
        self.plugin_manager.load_plugin(constant.BUILTIN_PLUGINS_DIR)
        # 加载自定义插件
        if self.config.app.plugins_dir:
            self.plugin_manager.load_plugin(self.config.app.plugins_dir)

        self.plugin_global_config = PluginGlobalConfig(
            info_dir=self.config.app.info_dir
        )

    def load_plugin(self, plugin_path: Path):
        """
        通过文件/目录加载插件

        :param plugin_path: 插件目录/文件路径
        """
        self.plugin_manager.load_plugin(plugin_path)

    def load_plugin_by_class(self, config_class: Any, plugin_class: Any):
        """
        通过类加载插件

        :param config_class: 插件配置类
        :param plugin_class: 插件类
        """
        self.plugin_manager.load_plugin_by_class(config_class, plugin_class)

    def run(self):
        """
        运行
        """
        try:
            logger.info("Running app...")
            logger.info(f"Configs: {self.config}")
            logger.info(f"Envs: {self.env}")
            logger.info(f"Args: {self.args}")

            # 创建流程
            self._create_flows()
            # 清空 info 目录
            self._clear_info_dir()
            # 执行流程
            self._execute_flows()

            logger.info("Running app finished")
        except Exception as e:
            logger.error(f"Running app failed: {e}")
            raise e
