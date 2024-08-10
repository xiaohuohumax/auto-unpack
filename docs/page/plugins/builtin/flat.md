---
icon: material/code-json
---

# Flat

!!! info "Flat 插件"

    Flat 插件用于扁平化文件结构，即将配置层级的文件移动根目录下。

## :link: 上下文

| 上下文 | 类型 | 描述 | 默认值 |
| ------ | ---- | ---- | ------ |

## :gear: 配置

### FlatPluginConfig

!!! info "FlatPluginConfig"

    `auto_unpack.plugins.empty.FlatPluginConfig`

| 名称                      | 类型            | 描述                           | 默认值   |
| ------------------------- | --------------- | ------------------------------ | -------- |
| :star: `name`             | Literal['flat'] | 插件名称，固定为 `'flat'`      | `'flat'` |
| :star: `dir`              | Path            | 需要扁平化的文件夹             | 无       |
| `depth`                   | Optional[int]   | 扁平化的深度，null：不限制深度 | 无       |
| [`上下文字段见上文`](#_1) |                 |                                |          |

## :recycle: 示例

### 将文件夹 output 中的所有文件移动到根目录下

```txt
output/
├── file1.txt
└── subfolder/
    └── file2.txt

# flat 后

output/
├── file1.txt
├── file2.txt
└── subfolder/

```

```yaml
flow:
  steps:
    # 使用 flat 插件
    - name: flat
      dir: output
```