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

| 名称                      | 类型                                           | 描述                                                                                                            | 默认值  |
| ------------------------- | ---------------------------------------------- | --------------------------------------------------------------------------------------------------------------- | ------- |
| :star: `name`             | Literal['log']                                 | 插件名称，固定为 `'log'`                                                                                        | `'log'` |
| `file_name`               | str                                            | 日志文件名                                                                                                      | `'log'` |
| `print_stats`             | List[Literal['all', 'ctime', 'mtime', 'size']] | 打印文件信息的字段<br/>`all`：所有信息<br/>`ctime`：创建时间<br/>`mtime`：修改时间<br/>`size`：文件大小（字节） | `[]`    |
| [`上下文字段见上文`](#_1) |                                                |                                                                                                                 |         |

## :recycle: 示例

### 打印文件夹 archive 下所有文件，并且打印创建时间和修改时间

```yaml
flow:
  steps:
    - name: scan
      dir: archive
    - name: log
      file_name: log
      print_stats:
        - ctime
        - mtime
```