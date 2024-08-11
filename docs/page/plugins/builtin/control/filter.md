---
icon: material/filter-check-outline
---

# Filter

!!! info "Filter 插件"

    Filter 插件依照配置过滤筛选上下文中的文件列表，并将符合条件的文件列表保存到上下文以供后续步骤使用。

## :link: 上下文

| 上下文        | 类型          | 描述                 | 默认值      |
| ------------- | ------------- | -------------------- | ----------- |
| `load_key`    | str           | 需要过滤的文件列表   | `'default'` |
| `save_key`    | str           | 过滤后保留的文件列表 | `'default'` |
| `exclude_key` | Optional[str] | 过滤后排除的文件列表 | 无          |

## :gear: 配置

### FilterPluginConfig

!!! info "FilterPluginConfig"

    `auto_unpack.plugins.control.filter.FilterPluginConfig`

| 名称                                                                    | 类型                                                                                                                        | 描述                            | 默认值     |
| ----------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- | ------------------------------- | ---------- |
| :star: `name`                                                           | Literal['filter']                                                                                                           | 插件名称，固定为 `'filter'`     | `'filter'` |
| :construction: `includes` `废弃`<br>`请使用`[`GlobFilter`](#globfilter) | List[str]                                                                                                                   | 包含的文件路径列表，glob 表达式 | `['**/*']` |
| :construction: `excludes` `废弃`<br>`请使用`[`GlobFilter`](#globfilter) | List[str]                                                                                                                   | 排除的文件路径列表，glob 表达式 | `[]`       |
| `rules`                                                                 | List[Union[[SizeFilter](#sizefilter), [GlobFilter](#globfilter), [CTimeFilter](#ctimefilter), [MTimeFilter](#mtimefilter)]] | 筛选规则                        | `[]`       |
| [`上下文字段见上文`](#_1)                                               |                                                                                                                             |                                 |            |

### SizeFilter

!!! info "SizeFilter"

    `auto_unpack.plugins.control.filter.SizeFilter` 文件大小过滤器，用于筛选文件大小满足条件的文件。

| 名称          | 类型                                      | 描述                          | 默认值   |
| ------------- | ----------------------------------------- | ----------------------------- | -------- |
| :star: `mode` | Literal['size']                           | 文件大小过滤，固定为 `'size'` | `'size'` |
| :star: `size` | float                                     | 文件大小限制                  | 无       |
| `operator`    | Literal['<', '>', '<=', '>=', '==', '!='] | 大小比较运算符                | `>=`     |
| `unit`        | Literal['b', 'kb', 'mb', 'gb', 'tb']      | 单位                          | `mb`     |

### GlobFilter

!!! info "GlobFilter"

    `auto_unpack.plugins.control.filter.GlobFilter` 文件路径过滤器，用于筛选文件路径满足条件的文件。

| 名称          | 类型            | 描述                            | 默认值     |
| ------------- | --------------- | ------------------------------- | ---------- |
| :star: `mode` | Literal['glob'] | 文件路径过滤，固定为 `'glob'`   | `'glob'`   |
| `includes`    | List[str]       | 包含的文件路径列表，glob 表达式 | `['**/*']` |
| `excludes`    | List[str]       | 排除的文件路径列表，glob 表达式 | `[]`       |

### CTimeFilter

!!! info "CTimeFilter"

    `auto_unpack.plugins.control.filter.CTimeFilter` 创建时间过滤器，用于筛选文件创建时间满足条件的文件。

| 名称          | 类型                                      | 描述                                                   | 默认值    |
| ------------- | ----------------------------------------- | ------------------------------------------------------ | --------- |
| :star: `mode` | Literal['ctime']                          | 创建时间过滤，固定为 `'ctime'`                         | `'ctime'` |
| :star: `time` | str                                       | 时间限制(格式: RFC3339)<br/>例如：2022-01-01T00:00:00Z | 无        |
| `operator`    | Literal['<', '>', '<=', '>=', '==', '!='] | 大小比较运算符                                         | `>=`      |

### MTimeFilter

!!! info "MTimeFilter"

    `auto_unpack.plugins.control.filter.MTimeFilter` 修改时间过滤器，用于筛选文件修改时间满足条件的文件。

| 名称          | 类型                                      | 描述                                                   | 默认值    |
| ------------- | ----------------------------------------- | ------------------------------------------------------ | --------- |
| :star: `mode` | Literal['mtime']                          | 修改时间过滤，固定为 `'mtime'`                         | `'mtime'` |
| :star: `time` | str                                       | 时间限制(格式: RFC3339)<br/>例如：2022-01-01T00:00:00Z | 无        |
| `operator`    | Literal['<', '>', '<=', '>=', '==', '!='] | 大小比较运算符                                         | `>=`      |

## :recycle: 示例

### 保留文件大小 大于等于 1MB 的 txt 和 md 文件，并排除名叫 README.md 文件

```yaml
flow:
  steps:
    - name: scan
      dir: archive
    - name: filter
      rules:
        - mode: glob
          includes:
            - '*.txt'
            - '*.md'
          excludes:
            - 'README.md'
        - mode: size
          size: 1.0
          operator: '>='
          unit: mb
```

### 打印 文件创建时间 在 2022-01-01 之后的文件

```yaml
flow:
  steps:
    - name: scan
      dir: archive
    - name: filter
      rules:
        - mode: ctime
          time: "2022-01-01T00:00:00Z"
          operator: ">="
    - name: log
```