---
icon: material/folder-remove-outline
---

# Empty

!!! info "Empty 插件"

    Empty 插件用于删除指定目录下的所有空文件夹。

## :link: 上下文

| 上下文 | 类型 | 描述 | 默认值 |
| ------ | ---- | ---- | ------ |

## :gear: 配置

### EmptyPluginConfig

!!! info "EmptyPluginConfig"

    `auto_unpack.plugins.empty.EmptyPluginConfig`

| 名称                      | 类型             | 描述                       | 默认值    |
| ------------------------- | ---------------- | -------------------------- | --------- |
| :star: `name`             | Literal['empty'] | 插件名称，固定为 `'empty'` | `'empty'` |
| :star: `dir`              | Path             | 需要清理空文件夹的目录     | 无        |
| [`上下文字段见上文`](#_1) |                  |                            |           |

## :recycle: 示例

### 清理文件夹 output 下的所有空文件夹

```yaml
flow:
  steps:
    - name: empty
      dir: output
```