import logging
import time
from typing import Any, List

from auto_unpack.plugin import OutputPluginConfig, Plugin, pluginManager

logger = logging.getLogger(__name__)


class LoopPluginConfig(OutputPluginConfig):
    """
    循环插件配置
    """
    # 步骤配置
    steps: List[Any] = []
    # 最大循环次数 -1不限制
    max_loops: int = 1024
    # 循环间隔时间 单位秒
    loop_interval: int = 1


class LoopPlugin(Plugin[LoopPluginConfig]):
    """
    循环插件

    作用：循环执行插件流程
    """
    name: str = "loop"
    flows: List[Plugin] = []

    def _create_flows(self):
        """
        根据配置创建流程
        """
        self.flows = []
        logger.info("Creating loop flows...")
        steps = self.config.steps
        for step in steps:
            plugin = pluginManager.create_plugin_instance(
                step, self.store, self.global_config
            )
            logger.debug(f"Flow step `{step.get('name')}` created")
            self.flows.append(plugin)

        logger.info(f"Flows created: {len(self.flows)}")

    def _execute_flows(self):
        """
        执行流程
        """
        logger.info("Executing loop flows...")
        flows_count = len(self.flows)
        for i, flow in enumerate(self.flows):
            logger.info(
                f"{i+1}/{flows_count} Executing flow `{flow.name}`")
            logger.debug(f'Config: {flow.config.dict()}')
            flow.execute()

    def init(self):
        self._create_flows()

    def execute(self):
        context = self.load_context()

        loop_index = 0
        while len(context.file_datas) > 0:
            self._execute_flows()
            context = self.load_context()

            if self.config.max_loops > 0 and loop_index >= self.config.max_loops:
                raise RuntimeError(
                    f"Loop plugin has reached the maximum number of loops: {self.config.max_loops}")

            time.sleep(self.config.loop_interval)
            loop_index += 1
