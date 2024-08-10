import json
import shutil
from pathlib import Path
from typing import Any, Dict

from auto_unpack import __version__ as version
from auto_unpack import constant, plugin, schema
from auto_unpack.util import file

schema_folder = Path("schema")
config_schema_name = "auto-unpack-schema.json"
config_schema_flow_name = "auto-unpack-flow-schema.json"


def clear_same_schema():
    """
    清理各版本间相同的 schema 文件

    多版本 schema 文件相同时只保留版本号最小的
    例如： 1.0.0 与 1.0.1 版本的 schema 文件只保留 1.0.0 版本的
    """
    version_folders = list(schema_folder.glob("*.*.*/"))

    if len(version_folders) <= 1:
        return

    def get_version(folder: Path) -> int:
        """
        获取版本号

        :param folder: 版本文件夹
        :return: 版本号
        """
        folder_items = folder.name.split(".")[::-1]
        return sum([int(v) * (1000 ** i) for i, v in enumerate(folder_items)])

    version_folders = sorted(
        version_folders, key=lambda v: get_version(v), reverse=True)

    before_folder = version_folders[0]
    before_config = file.read_file(before_folder/config_schema_name)
    before_flow = file.read_file(before_folder/config_schema_flow_name)

    remove_folders = []

    for version_folder in version_folders[1:]:
        now_config = file.read_file(version_folder/config_schema_name)
        now_flow = file.read_file(version_folder/config_schema_flow_name)

        if before_config == now_config and before_flow == now_flow:
            remove_folders.append(before_folder)

        before_folder = version_folder
        before_config = now_config
        before_flow = now_flow

    for remove_folder in remove_folders:
        shutil.rmtree(remove_folder)


def write_schema_file(schema_dict: Dict[str, Any], file_path: Path):
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
        config_json_schema = schema.generate_config_schema()

        write_schema_file(config_json_schema, schema_folder/config_schema_name)
        write_schema_file(
            config_json_schema,
            schema_folder/version/config_schema_name
        )
        print(f"config schema generated: {schema_folder/config_schema_name}")

        plugin_manager = plugin.PluginManager()
        plugin_manager.load_plugin(constant.BUILTIN_PLUGINS_DIR)

        # 流程配置文件 schema
        flow_json_schema = schema.generate_flow_schema(
            plugin_manager=plugin_manager
        )
        write_schema_file(
            flow_json_schema,
            schema_folder/config_schema_flow_name
        )
        write_schema_file(
            flow_json_schema,
            schema_folder/version/config_schema_flow_name
        )

        # 清理相同 schema 文件
        clear_same_schema()

        print(
            f"flow schema generated: {schema_folder/config_schema_flow_name}")

        print("auto-unpack schema generated successfully.")
    except Exception as e:
        print(f"Failed to generate auto-unpack schema: {e}")
