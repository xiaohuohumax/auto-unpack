import json
from pathlib import Path
from typing import Any, List, Union

import toml
from pydantic import Field, create_model
from pydantic.json_schema import GenerateJsonSchema
from pydantic_core.core_schema import ListSchema

from auto_unpack import config, plugin
from auto_unpack.util import file

schema_folder = Path("schema")
config_schema_name = "auto-unpack-schema.json"
config_schema_flow_name = "auto-unpack-flow-schema.json"
pyproject = toml.load(Path("pyproject.toml"))
version = pyproject["project"]["version"]
plugin_folders = [
    Path("auto_unpack/plugins")
]

# 默认至生成内置插件的 json schema
plugin_manager = plugin.pluginManager
for plugin_folder in plugin_folders:
    plugin_manager.load_plugin(plugin_folder)

CustomStep = create_model(
    "CustomStep",
    name=(str, Field(..., description="自定义插件")),
)
# 步骤配置
step_classes = [CustomStep]
# 步骤名称
step_names = []


class CustomSchemaGenerator(GenerateJsonSchema):
    """
    自定义 schema 生成器
    """

    def literal_schema(self, schema: ListSchema):
        """
        处理 Literal 类型，将 const 类型中的 enum 属性删除
        """
        res = super().literal_schema(schema)
        if 'const' in res:
            del res['enum']
        return res

    def nullable_schema(self, schema):
        """
        处理 optional 类型，将 anyOf 类型转换为 oneOf 类型
        """
        schema = super().nullable_schema(schema)
        if 'anyOf' in schema:
            schema['oneOf'] = schema.pop('anyOf')
        return schema

    def union_schema(self, schema):
        """
        处理 union 类型，将所有 anyOf 类型转换为 oneOf 类型
        """
        schema = super().union_schema(schema)
        if 'anyOf' in schema:
            schema['oneOf'] = schema.pop('anyOf')
        return schema


for plugin_config, plugin_class in plugin_manager.plugins:
    name = plugin_class.name
    attr = {}
    if name == "loop":
        attr['steps'] = (List['Step_Type'], Field(..., description="循环步骤"))

    plugin_config_schema = create_model(
        plugin_config.__name__,
        __base__=plugin_config,
        **attr
    )

    step_names.append(name)
    step_classes.append(plugin_config_schema)

Step_Type = Union[tuple(step_classes)]

FlowConfig = create_model(
    "FlowConfig",
    steps=(List[Step_Type], Field(...,
           description="流程步骤", discriminator="name"))
)
FlowConfig.__doc__ = "流程配置"

ProjectFlowConfig = create_model(
    "ProjectFlowConfig",
    flow=(FlowConfig, Field(..., description="流程配置"))
)
ProjectFlowConfig.__doc__ = "项目流程配置"


def write_schema_file(schema_dict: Any, file_path: Path):
    """
    写入 schema 文件

    :param schema_dict: schema dict
    :param file_path: 文件路径
    """
    schema = json.dumps(schema_dict, ensure_ascii=False, indent=4)
    file.write_file(file_path, schema)


if __name__ == '__main__':
    try:
        print("generating auto-unpack schema...")
        print(f"version: {version}")
        # 配置文件 schema
        config_json_schema = config.ProjectConfig.model_json_schema(
            schema_generator=CustomSchemaGenerator
        )

        write_schema_file(config_json_schema, schema_folder/config_schema_name)
        write_schema_file(
            config_json_schema,
            schema_folder/version/config_schema_name
        )
        print(f"config schema generated: {schema_folder/config_schema_name}")

        # 流程配置文件 schema
        flow_json_schema = ProjectFlowConfig.model_json_schema(
            schema_generator=CustomSchemaGenerator
        )
        # 自定义插件需要排除已有插件名称
        flow_json_schema['$defs'][CustomStep.__name__]['properties']['name']['not'] = {
            "enum": step_names
        }
        write_schema_file(
            flow_json_schema,
            schema_folder/config_schema_flow_name
        )
        write_schema_file(
            flow_json_schema,
            schema_folder/version/config_schema_flow_name
        )
        print(
            f"flow schema generated: {schema_folder/config_schema_flow_name}")

        print("auto-unpack schema generated successfully.")
    except Exception as e:
        print(f"Failed to generate auto-unpack schema: {e}")
