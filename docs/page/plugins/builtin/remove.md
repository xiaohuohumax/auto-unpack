---
icon: material/delete-empty-outline
---

# Remove

!!! info "Remove 插件"

    Remove 插件用于删除指定上下文的文件列表，删除后清空上下文。

## :link: 上下文

| 上下文     | 类型 | 描述             | 默认值      |
| ---------- | ---- | ---------------- | ----------- |
| `load_key` | str  | 要删除的文件列表 | `'default'` |

## :gear: 配置

### RemovePluginConfig

!!! info "RemovePluginConfig"

    `auto_unpack.plugins.remove.RemovePluginConfig`

| 名称                      | 类型              | 描述                        | 默认值     |
| ------------------------- | ----------------- | --------------------------- | ---------- |
| :star: `name`             | Literal['remove'] | 插件名称，固定为 `'remove'` | `'remove'` |
| [`上下文字段见上文`](#_1) |                   |                             |            |

## :recycle: 示例

### 删除文件夹 output 下全部的 txt 文件

```yaml
flow:
  steps:
    # 扫描 output 文件夹下所有 txt 文件
    - name: scan
      dir: output
      includes: 
        - "*.txt"
    # 删除扫描到的 txt 文件
    - name: remove
```