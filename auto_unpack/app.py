import logging
import shutil
from pathlib import Path
from typing import Any, List

from pydantic import BaseModel

from .args import args
from .config import config, load_config_by_class
from .env import env
from .plugin import Plugin, PluginGlobalConfig, pluginManager
from .store import DataStore

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

    # 插件目录
    plugins_dir: Path = Path(__file__).parent/'plugin'
    # 流程(插件实例)
    flows: List[Plugin] = []
    # 数据仓库(插件间共享数据)
    store: DataStore = DataStore()
    # 插件全局配置
    plugin_global_config: PluginGlobalConfig

    def create_flows(self):
        """
        根据配置创建流程
        """
        self.flows = []
        logger.info("Creating flows...")
        flow_config = load_config_by_class(ProjectFlowConfig)
        steps = flow_config.flow.steps
        for step in steps:
            plugin = pluginManager.create_plugin(
                step, self.store, self.plugin_global_config
            )
            logger.debug(f"Flow step `{step.get('name')}` created")
            self.flows.append(plugin)

        logger.info(f"Flows created: {len(self.flows)}")

    def execute_flows(self):
        """
        执行流程
        """
        if config.app.clear_info_dir:
            logger.info("Clearing info dir...")
            shutil.rmtree(config.app.info_dir, ignore_errors=True)

        config.app.info_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Executing flows...")
        flows_count = len(self.flows)
        for i, flow in enumerate(self.flows):
            logger.info(f"{i+1}/{flows_count} Executing flow `{flow.name}`")
            logger.debug(f'Config: {flow.config.dict()}')
            flow.execute()

    def __init__(self):
        logger.info("Initializing app...")
        self.plugin_global_config = PluginGlobalConfig(
            info_dir=config.app.info_dir
        )
        # 创建流程
        self.create_flows()

    def run(self):
        """
        运行
        """
        try:
            logger.info("Running app...")

            logger.info(f"Configs: {config}")
            logger.info(f"Envs: {env}")
            logger.info(f"Args: {args}")

            # 执行流程
            self.execute_flows()

            logger.info("Running app finished")
        except Exception as e:
            logger.error(f"Running app failed: {e}")
            raise e
