# 配置校验

给配置文件添加校验功能，可以有效避免配置错误导致程序运行异常。

## JSON Schema 文件

| Schema 文件名                | 作用                                        |
| ---------------------------- | ------------------------------------------- |
| auto-unpack-schema.json      | 项目配置校验（application.yaml）            |
| auto-unpack-flow-schema.json | 验证流程配置校验（application.[mode].yaml） |

### CDN 地址

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

### Github 地址

```txt
<!-- 最新 -->
https://github.com/xiaohuohumax/auto-unpack/tree/main/schema/auto-unpack-schema.json
<!-- 特定版本 -->
https://github.com/xiaohuohumax/auto-unpack/tree/main/schema/[version]/auto-unpack-schema.json

<!-- 最新 -->
https://github.com/xiaohuohumax/auto-unpack/tree/main/schema/auto-unpack-flow-schema.json
<!-- 特定版本 -->
https://github.com/xiaohuohumax/auto-unpack/tree/main/schema/[version]/auto-unpack-flow-schema.json
```

## VSCode 中使用

1. 安装插件 `redhat.vscode-yaml`
2. 添加校验映射配置 `.vscode/settings.json`
```json
{
     "yaml.schemas": {
        // cdn
        // "https://cdn.jsdelivr.net/gh/xiaohuohumax/auto-unpack@main/schema/auto-unpack-schema.json": "config/application.yaml",
        // "https://cdn.jsdelivr.net/gh/xiaohuohumax/auto-unpack@main/schema/auto-unpack-flow-schema.json": "config/application.*.yaml",
        // local
        "schema/auto-unpack-schema.json": "config/application.yaml",
        "schema/auto-unpack-flow-schema.json": "config/application.*.yaml",
     },
}
```

## 构建 JSON Schema


```python
import json
from pathlib import Path
from typing import Literal

from pydantic import Field

from auto_unpack.plugin import PluginConfig, Plugin, PluginManager
from auto_unpack import constant, schema
from auto_unpack.util import file


class MyConfig(PluginConfig):
    name: Literal['my'] = Field(
        default='my',
        description="我的插件"
    )


class MyPlugin(Plugin[MyConfig]):

    name: str = 'my'

    def init(self):
        print("MyPlugin init")

    def execute(self):
        print("MyPlugin execute")


if __name__ == '__main__':
    # 插件管理
    plugin_manager = PluginManager()
    # 添加内置插件
    plugin_manager.load_plugin(constant.BUILTIN_PLUGINS_DIR)
    # 添加自己新插件
    plugin_manager.load_plugin_by_class(MyConfig, MyPlugin)

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