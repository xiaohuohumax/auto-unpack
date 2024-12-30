from typing import Any, Dict, List, Union

from pydantic import Field, create_model
from pydantic.json_schema import GenerateJsonSchema

from . import config
from .plugin import PluginManager


class CustomSchemaGenerator(GenerateJsonSchema):
    """
    自定义 schema 生成器
    """

    def nullable_schema(self, schema):
        """
        处理 optional 类型，将 anyOf 类型转换为 oneOf 类型
        """
        schema = super().nullable_schema(schema)
        if "anyOf" in schema:
            schema["oneOf"] = schema.pop("anyOf")
        return schema

    def union_schema(self, schema):
        """
        处理 union 类型，将所有 anyOf 类型转换为 oneOf 类型
        """
        schema = super().union_schema(schema)
        if "anyOf" in schema:
            schema["oneOf"] = schema.pop("anyOf")
        return schema


def generate_config_schema() -> Dict[str, Any]:
    """
    生成配置文件 schema

    :return: 配置文件 schema
    """
    return config.ProjectConfig.model_json_schema(
        schema_generator=CustomSchemaGenerator
    )


def generate_flow_schema(plugin_manager: PluginManager) -> Dict[str, Any]:
    """
    生成流程配置文件 schema

    :param plugin_manager: 插件管理器
    :return: 流程配置文件 schema
    """
    global Step_Type
    CustomStep = create_model(
        "CustomStep",
        name=(str, Field(description="自定义插件")),
    )
    # 步骤配置
    step_classes = [CustomStep]
    # 步骤名称
    step_names = []

    for plugin_config, plugin_class in plugin_manager.plugins:
        name = plugin_class.name
        attr = {}
        if name == "loop":
            attr["steps"] = ("Step_Type", Field(description="循环步骤"))

        plugin_config_schema = create_model(
            plugin_config.__name__, __base__=plugin_config, **attr
        )

        step_names.append(name)
        step_classes.append(plugin_config_schema)

    Step_Type = List[Union[tuple(step_classes)]]

    FlowConfig = create_model(
        "FlowConfig", steps=(Step_Type, Field(description="流程步骤"))
    )
    FlowConfig.__doc__ = "流程配置"

    ProjectFlowConfig = create_model(
        "ProjectFlowConfig", flow=(FlowConfig, Field(description="流程配置"))
    )
    ProjectFlowConfig.__doc__ = "项目流程配置"

    # 流程配置文件 schema
    flow_json_schema = ProjectFlowConfig.model_json_schema(
        schema_generator=CustomSchemaGenerator
    )
    # 自定义插件需要排除已有插件名称
    flow_json_schema["$defs"][CustomStep.__name__]["properties"]["name"]["not"] = {
        "enum": step_names
    }

    return flow_json_schema
