---
icon: material/file-arrow-left-right-outline
---

# Transfer

!!! info "Transfer 插件"

    Transfer 插件用于转移上下文中的文件列表。

## :link: 上下文

| 上下文     | 类型 | 描述             | 默认值      |
| ---------- | ---- | ---------------- | ----------- |
| `load_key` | str  | 要转移的文件列表 | `'default'` |
| `save_key` | str  | 转移后的文件列表 | `'default'` |

## :gear: 配置

### TransferPluginConfig

!!! info "TransferPluginConfig"

    `auto_unpack.plugins.transfer.TransferPluginConfig`

| 名称                      | 类型                                   | 描述                                                                 | 默认值       |
| ------------------------- | -------------------------------------- | -------------------------------------------------------------------- | ------------ |
| :star: `name`             | Literal['transfer']                    | 插件名称，固定为 `'transfer'`                                        | `'transfer'` |
| :star: `mode`             | Literal['move', 'copy']                | 转移模式<br/>`move`：移动<br/>`copy`：复制                           | 无           |
| :star: `target_dir`       | Path                                   | 目标路径                                                             | 无           |
| `keep_structure`          | bool                                   | 是否保持目录结构，相对于扫描路径                                     | `true`       |
| `overwrite_mode`          | Literal['rename', 'overwrite', 'skip'] | 覆盖模式<br/>`rename`：重命名<br/>`overwrite`：覆盖<br/>`skip`：跳过 | `'rename'`   |
| [`上下文字段见上文`](#_1) |                                        |                                                                      |              |

## :recycle: 示例

### 将文件夹 archive 中的所有文件复制到 output 文件夹下

```yaml
flow:
  steps:
    # 扫描 archive 文件夹
    - name: scan
      dir: archive

    # 将扫描的文件复制到 output 文件夹下
    - name: transfer
      mode: copy
      target_dir: output
```