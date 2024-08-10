---
icon: material/clipboard-edit-outline
---

# Log

!!! info "Log 插件"

    Log 插件用于打印上下文中的文件信息。

## :link: 上下文

| 上下文     | 类型 | 描述             | 默认值      |
| ---------- | ---- | ---------------- | ----------- |
| `load_key` | str  | 要打印的文件列表 | `'default'` |

## :gear: 配置

### LogPluginConfig

!!! info "LogPluginConfig"

    `auto_unpack.plugins.log.LogPluginConfig`

| 名称                      | 类型           | 描述                     | 默认值  |
| ------------------------- | -------------- | ------------------------ | ------- |
| :star: `name`             | Literal['log'] | 插件名称，固定为 `'log'` | `'log'` |
| `file_name`               | str            | 日志文件名               | `'log'` |
| [`上下文字段见上文`](#_1) |                |                          |         |

## :recycle: 示例

### 打印文件夹 archive 下所有文件

```yaml
flow:
  steps:
    - name: scan
      dir: archive
    - name: log
      file_name: log
```