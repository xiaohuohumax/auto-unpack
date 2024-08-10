import json
from pathlib import Path

from auto_unpack import constant, plugin, schema
from auto_unpack.util import file

config_schema_flow_path = Path("schema/auto-unpack-flow-schema.json")

if __name__ == '__main__':
    try:
        print("generating custom-plugin schema...")

        plugin_manager = plugin.PluginManager()
        # 内置插件
        plugin_manager.load_plugin(constant.BUILTIN_PLUGINS_DIR)
        # 自定义插件
        plugin_manager.load_plugin(Path("plugins"))

        flow_json_schema = schema.generate_flow_schema(
            plugin_manager=plugin_manager
        )

        schema = json.dumps(flow_json_schema, ensure_ascii=False, indent=4)
        file.write_file(config_schema_flow_path, schema)
        print(f"flow schema generated: {config_schema_flow_path}")

        print("custom-plugin schema generated successfully.")
    except Exception as e:
        print(f"Failed to generate custom-plugin schema: {e}")
