---
hide:
  - navigation
---

# 自定义插件

除了默认的内置插件外，你还可以编写自己的插件。

!!! tip "提示"

    下面将以编写一个打印插件为例，介绍如何编写一个自定义插件。也可以直接参考 [自定义插件模板项目](https://github.com/xiaohuohumax/auto-unpack/tree/main/release/template/custom-plugin/){target=_blank}。

## 插件目录

项目下添加 `plugins` 目录

```sh
mkdir plugins
```

<!-- todo: 添加插件相关类的介绍 -->

## 编写插件

`plugins/print.py`

```python
import logging
from typing import Literal

from pydantic import Field

from auto_unpack.plugin import Plugin, PluginConfig

logger = logging.getLogger(__name__)


class PrintPluginConfig(PluginConfig):
    """
    打印插件配置
    """
    name: Literal["print"] = Field(
        default="print",
        description="打印插件"
    )
    message: str = Field(
        default="Hello, world!",
        description="打印的消息"
    )


class PrintPlugin(Plugin[PrintPluginConfig]):
    """
    打印插件
    """
    name: str = "print"

    def init(self):
        """
        初始化打印插件
        """
        logger.debug("init print plugin")

    def execute(self):
        """
        执行打印插件
        """
        logger.info(self.config.message)

```

## 添加插件

插件添加方式多样，以下方式任选其一即可。

=== "配置文件添加"

    `config/application.yaml`

    ```yaml hl_lines="2-3"
    app:
      # 添加自定义插件目录
      plugins_dir: plugins

    ```

=== "代码添加"

    `app/__main__.py`

    ```python hl_lines="1 4 8-13"
    from pathlib import Path

    from auto_unpack import App
    from ..plugins.print import PluginConfig, PrintPlugin

    if __name__ == '__main__':
        app = App()
        # 通过目录加载插件
        app.load_plugin(Path("plugins"))
        # 通过文件加载插件
        app.load_plugin(Path("plugins/print.py"))
        # 通过类加载插件
        app.load_plugin_by_class(PluginConfig, PrintPlugin)
        app.run()
    ```

## 使用插件

`config/application.prod.yaml`

```yaml hl_lines="3-4"
flow:
  steps:
    - name: print
      message: "Hello, world!"
```

## 构建约束

自定义插件可以构建约束，以确保插件的配置符合预期。

[构建 JSON Schema](../schema.md#json-schema_1)
