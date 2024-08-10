---
icon: material/source-merge
---

# Merge

!!! info "Merge 插件"

    Merge 插件用于合并多个上下文中的文件列表，并保存到新的上下文中。

## :link: 上下文

| 上下文         | 类型      | 描述                   | 默认值      |
| -------------- | --------- | ---------------------- | ----------- |
| `save_key`     | str       | 合并后的文件列表       | `'default'` |
| `context_keys` | List[str] | 需要合并的文件列表集合 | `[]`        |

## :gear: 配置

### MergePluginConfig


!!! info "MergePluginConfig"

    `auto_unpack.plugins.control.merge.MergePluginConfig`

| 名称                      | 类型             | 描述                       | 默认值    |
| ------------------------- | ---------------- | -------------------------- | --------- |
| :star: `name`             | Literal['merge'] | 插件名称，固定为 `'merge'` | `'merge'` |
| [`上下文字段见上文`](#_1) |                  |                            |           |

## :recycle: 示例

### 将扫描到的 txt 和 md 文件合并到 'default' 上下文中

```yaml
flow:
  steps:
    # 扫描 txt 文件，保存到 txt_context 上下文
    - name: scan
      dir: archive
      includes:
        - '*.txt'
      save_key: txt_context

    # 日志打印 txt_context 上下文内容
    - name: log
      load_key: txt_context
      file_name: txt_files

    # 扫描 md 文件，保存到 md_context 上下文
    - name: scan
      dir: archive
      includes:
        - '*.md'
      save_key: md_context

    # 日志打印 md_context 上下文内容
    - name: log
      load_key: md_context
      file_name: md_files

    # 使用 merge 插件合并两个上下文到默认（default）上下文
    - name: merge
      # save_key: ...
      context_keys:
        - txt_context
        - md_context

    # 日志打印合并后的上下文内容
    - name: log
      file_name: merged
```