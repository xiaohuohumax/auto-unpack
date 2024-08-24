---
hide:
  - navigation
---

# 配置约束

给配置文件添加约束功能，可以有效避免配置错误导致程序运行异常。

## JSON Schema 约束文件

| 文件名                       | 作用                                        |
| ---------------------------- | ------------------------------------------- |
| auto-unpack-schema.json      | 项目配置约束（application.yaml）            |
| auto-unpack-flow-schema.json | 验证流程配置约束（application.[mode].yaml） |

!!! warning "注意事项"

    约束文件生成规则，有变化才会生成对应版本的约束文件。所以未发现与当前版本号相同的约束文件时，请使用小于或等于当前版本号的最接近的版本号。

    例如：当前版本：2.11.0，约束文件版本：【...，2.7.0，2.8.0，2.9.0，2.14.0】，则使用版本号 2.9.0 即可。

=== "jsDelivr"

    ```txt
    <!-- 最新 -->
    https://cdn.jsdelivr.net/gh/xiaohuohumax/auto-unpack@main/schema/auto-unpack-schema.json
    <!-- 特定版本 -->
    https://cdn.jsdelivr.net/gh/xiaohuohumax/auto-unpack@main/schema/[version]/auto-unpack-schema.json

    <!-- 最新 -->
    https://cdn.jsdelivr.net/gh/xiaohuohumax/auto-unpack@main/schema/auto-unpack-flow-schema.json
    <!-- 特定版本 -->
    https://cdn.jsdelivr.net/gh/xiaohuohumax/auto-unpack@main/schema/[version]/auto-unpack-flow-schema.json
    ```

=== "Github"

    ```txt
    <!-- 最新 -->
    https://raw.githubusercontent.com/xiaohuohumax/auto-unpack/main/schema/auto-unpack-schema.json
    <!-- 特定版本 -->
    https://raw.githubusercontent.com/xiaohuohumax/auto-unpack/main/schema/[version]/auto-unpack-schema.json

    <!-- 最新 -->
    https://raw.githubusercontent.com/xiaohuohumax/auto-unpack/main/schema/auto-unpack-flow-schema.json
    <!-- 特定版本 -->
    https://raw.githubusercontent.com/xiaohuohumax/auto-unpack/main/schema/[version]/auto-unpack-flow-schema.json

    ```

## VSCode 中使用 Schema

安装插件 [redhat.vscode-yaml](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml){target=_blank}

添加约束映射 `.vscode/settings.json`

```json
{
    "yaml.schemas": {
        // cdn
        // "https://cdn.jsdelivr.net/gh/xiaohuohumax/auto-unpack@main/schema/auto-unpack-schema.json": "config/application.yaml",
        // "https://cdn.jsdelivr.net/gh/xiaohuohumax/auto-unpack@main/schema/auto-unpack-flow-schema.json": "config/application.*.yaml",
        // github
        // "https://raw.githubusercontent.com/xiaohuohumax/auto-unpack/main/schema/auto-unpack-schema.json": "config/application.yaml",
        // "https://raw.githubusercontent.com/xiaohuohumax/auto-unpack/main/schema/auto-unpack-flow-schema.json": "config/application.*.yaml",
        // local
        "schema/auto-unpack-schema.json": "config/application.yaml",
        "schema/auto-unpack-flow-schema.json": "config/application.*.yaml",
    },
}
```

## 构建 JSON Schema

!!! warning "注意事项"

    默认的 JSON Schema 只包含内置插件的配置项，如果需要添加自定义插件的配置项，可以根据需要修改然后重新构建。


=== "通过脚手架工具构建"

    ```sh
    # auto-unpack schema -h 查看帮助

    # 插件路径可以多个，路径可以是文件夹或文件
    # 例如：auto-unpack schema plugins/ print.py
    auto-unpack schema plugins

    # 忽略内置插件，默认：False
    auto-unpack schema plugins -i

    # 输出到指定文件，默认：schema/auto-unpack-flow-schema.json
    auto-unpack schema plugins -o schema.json
    ```

=== "通过编写代码构建"

    ```python
    import json
    import logging
    from pathlib import Path
    from typing import Literal

    from pydantic import Field

    from auto_unpack.plugin import PluginConfig, Plugin, PluginManager
    from auto_unpack import constant, schema
    from auto_unpack.util import file


    class PrintPluginConfig(PluginConfig):
        """
        打印插件配置
        """
        name: Literal["print"] = Field(
            default="print",
            description="打印插件"
        )
        ...


    class PrintPlugin(Plugin[PrintPluginConfig]):
        """
        打印插件
        """
        name: str = "print"
        ...


    if __name__ == '__main__':
        # 插件管理
        plugin_manager = PluginManager()
        # 添加内置插件
        plugin_manager.load_plugin(constant.BUILTIN_PLUGINS_DIR)
        # 通过文件夹添加插件
        # plugin_manager.load_plugin(Path('plugins'))
        # 通过文件添加插件
        # plugin_manager.load_plugin(Path('plugins/print.py'))
        # 添加自己新插件
        plugin_manager.load_plugin_by_class(PrintPluginConfig, PrintPlugin)

        # auto-unpack-flow-schema.json
        flow_schema_dict = schema.generate_flow_schema(
            plugin_manager=plugin_manager
        )

        flow_schema = json.dumps(flow_schema_dict, indent=4, ensure_ascii=False)
        file.write_file(Path('auto-unpack-flow-schema.json'), flow_schema)

        # auto-unpack-schema.json
        # flow_config_dict = schema.generate_config_schema()

        # config_schema = json.dumps(flow_config_dict, indent=4, ensure_ascii=False)
        # file.write_file(Path('auto-unpack-schema.json'), config_schema)
    ```
