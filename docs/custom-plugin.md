# 扩展插件

## 加载插件

### 通过类加载插件

```python
from typing import Literal

from pydantic import Field

from auto_unpack import App
from auto_unpack.plugin import PluginConfig, Plugin


class MyConfig(PluginConfig):
    name: Literal['my'] = Field(
        default='my',
        description='我的插件'
    )


class MyPlugin(Plugin[MyConfig]):
    name: str = "my"

    def init(self):
        print("my plugin init")

    def execute(self):
        print("my plugin execute")


if __name__ == '__main__':
    app = App()
    # 通过类加载插件
    app.load_plugin_by_class(MyConfig, MyPlugin)
    # 运行程序
    app.run()
```
配置使用

```yaml
flow:
  steps:
    - name: my
      ...
```

### 通过插件文件/目录加载插件

plugins/my.py

```python
from typing import Literal

from pydantic import Field

from auto_unpack.plugin import PluginConfig, Plugin


class MyConfig(PluginConfig):
    name: Literal['my'] = Field(
        default='my',
        description='我的插件'
    )


class MyPlugin(Plugin[MyConfig]):
    name: str = "my"

    def init(self):
        print("my plugin init")

    def execute(self):
        print("my plugin execute")
```

main.py

```python
from pathlib import Path
from auto_unpack import App

if __name__ == '__main__':
    app = App()
    # 通过配置文件/目录加载插件
    app.load_plugin(Path('./plugins'))
    app.load_plugin(Path('./plugins/my.py'))
    # 运行程序
    app.run()
```

配置使用

```yaml
flow:
  steps:
    - name: my
      ...
```