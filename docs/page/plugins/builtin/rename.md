---
icon: material/rename
---

# Rename

!!! info "Rename 插件"

    Rename 插件用于修改上下文中的文件的名称。

## :link: 上下文

| 上下文     | 类型 | 描述             | 默认值      |
| ---------- | ---- | ---------------- | ----------- |
| `load_key` | str  | 要改名的文件列表 | `'default'` |
| `save_key` | str  | 改名后的文件列表 | `'default'` |

## :gear: 配置

### RenamePluginConfig

!!! info "RenamePluginConfig"

    `auto_unpack.plugins.rename.RenamePluginConfig`

| 名称                      | 类型                                                        | 描述                        | 默认值     |
| ------------------------- | ----------------------------------------------------------- | --------------------------- | ---------- |
| :star: `name`             | Literal['rename']                                           | 插件名称，固定为 `'rename'` | `'rename'` |
| `rules`                   | List[Union[[ReplaceRule](#replacerule), [ReRule](#rerule)]] | 改名规则                    | `[]`       |
| [`上下文字段见上文`](#_1) |                                                             |                             |            |

### ReplaceRule

!!! info "ReplaceRule"

    `auto_unpack.plugins.rename.ReplaceRule`

| 名称             | 类型               | 描述                         | 默认值      |
| ---------------- | ------------------ | ---------------------------- | ----------- |
| :star: `mode`    | Literal['replace'] | 替换规则，固定为 `'replace'` | `'replace'` |
| :star: `search`  | str                | 匹配字符串                   | 无          |
| :star: `replace` | str                | 替换字符串                   | 无          |
| `count`          | int                | 替换次数，-1 表示全部替换    | `-1`        |

### ReRule

!!! info "ReRule"

    `auto_unpack.plugins.rename.ReRule`

| 名称             | 类型          | 描述                                                                                                                                    | 默认值 |
| ---------------- | ------------- | --------------------------------------------------------------------------------------------------------------------------------------- | ------ |
| :star: `mode`    | Literal['re'] | 正则规则，固定为 `'re'`                                                                                                                 | `'re'` |
| :star: `pattern` | str           | 正则表达式                                                                                                                              | 无     |
| :star: `replace` | str           | 替换字符串                                                                                                                              | 无     |
| `count`          | int           | 替换次数，0：不限次数                                                                                                                   | `0`    |
| `flags`          | str           | 正则表达式匹配模式<br/>`a`：ASCII 匹配模式<br/>`i`：忽略大小写<br/>`u`：Unicode 匹配模式<br/>例如：`iu` [忽略大小写、匹配 Unicode 字符] | `''`   |

## :recycle: 示例

### 删除文件名中的 '删除' 字样

```yaml
flow:
  steps:
    # 扫描 output 文件夹下所有文件
    - name: scan
      dir: output

    # 改名
    - name: rename
      rules:
        - mode: re
          pattern: 删除
          replace: ""
```

### 将文件按新规则重新命名

例如：`[test][2021_01_01].txt` 改为 `test-2021_01_01.txt`

```yaml
flow:
  steps:
    # 扫描 output 文件夹下所有文件
    - name: scan
      dir: output

    # 改名
    - name: rename
      rules:
        - mode: re
          pattern: \[(\w+)\]\[(.*)\]\.(\w+)
          replace: \1-\2.\3
```