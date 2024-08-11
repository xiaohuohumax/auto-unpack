---
icon: material/source-branch
---

# Switch

!!! info "Switch 插件"

    Switch 插件用于根据条件分支筛选上下文的文件列表，满足条件的文件列表将保存至对应的上下文，未满足条件的文件列表将保存至 `default_key` 上下文。

## :link: 上下文

| 上下文        | 类型 | 描述                         | 默认值      |
| ------------- | ---- | ---------------------------- | ----------- |
| `load_key`    | str  | 需要分支处理的文件列表       | `'default'` |
| `default_key` | str  | 未满足任意分支条件的文件列表 | 无          |

## :gear: 配置

### SwitchPluginConfig

!!! info "SwitchPluginConfig"

    `auto_unpack.plugins.control.switch.SwitchPluginConfig`

| 名称                      | 类型                                                                                                        | 描述                        | 默认值     |
| ------------------------- | ----------------------------------------------------------------------------------------------------------- | --------------------------- | ---------- |
| :star: `name`             | Literal['switch']                                                                                           | 插件名称，固定为 `'switch'` | `'switch'` |
| `cases`                   | List[Union[[SizeCase](#sizecase), [GlobCase](#globcase), [CTimeCase](#ctimecase), [MTimeCase](#mtimecase)]] | 分支条件                    | `[]`       |
| [`上下文字段见上文`](#_1) |                                                                                                             |                             |            |

### SizeCase

!!! info "SizeCase"

    `auto_unpack.plugins.control.switch.SizeCase` 文件大小过滤器，用于筛选文件大小满足条件的文件。

| 名称              | 类型                                      | 描述                          | 默认值   |
| ----------------- | ----------------------------------------- | ----------------------------- | -------- |
| :star: `mode`     | Literal['size']                           | 文件大小过滤，固定为 `'size'` | `'size'` |
| :star: `size`     | float                                     | 文件大小限制                  | 无       |
| `operator`        | Literal['<', '>', '<=', '>=', '==', '!='] | 大小比较运算符                | `>=`     |
| `unit`            | Literal['b', 'kb', 'mb', 'gb', 'tb']      | 单位                          | `mb`     |
| :star: `save_key` | str                                       | 分支上下文                    | 无       |


### GlobCase

!!! info "GlobCase"

    `auto_unpack.plugins.control.switch.GlobCase` 文件路径过滤器，用于筛选文件路径满足条件的文件。

| 名称              | 类型            | 描述                            | 默认值     |
| ----------------- | --------------- | ------------------------------- | ---------- |
| :star: `mode`     | Literal['glob'] | 文件路径过滤，固定为 `'glob'`   | `'glob'`   |
| `includes`        | List[str]       | 包含的文件路径列表，glob 表达式 | `['**/*']` |
| `excludes`        | List[str]       | 排除的文件路径列表，glob 表达式 | `[]`       |
| :star: `save_key` | str             | 分支上下文                      | 无         |

### CTimeCase

!!! info "CTimeCase"

    `auto_unpack.plugins.control.filter.CTimeCase` 创建时间过滤器，用于筛选文件创建时间满足条件的文件。

| 名称          | 类型                                      | 描述                                                   | 默认值    |
| ------------- | ----------------------------------------- | ------------------------------------------------------ | --------- |
| :star: `mode` | Literal['ctime']                          | 创建时间过滤，固定为 `'ctime'`                         | `'ctime'` |
| :star: `time` | str                                       | 时间限制(格式: RFC3339)<br/>例如：2022-01-01T00:00:00Z | 无        |
| `operator`    | Literal['<', '>', '<=', '>=', '==', '!='] | 大小比较运算符                                         | `>=`      |

### MTimeCase

!!! info "MTimeCase"

    `auto_unpack.plugins.control.filter.MTimeCase` 修改时间过滤器，用于筛选文件修改时间满足条件的文件。

| 名称          | 类型                                      | 描述                                                   | 默认值    |
| ------------- | ----------------------------------------- | ------------------------------------------------------ | --------- |
| :star: `mode` | Literal['mtime']                          | 修改时间过滤，固定为 `'mtime'`                         | `'mtime'` |
| :star: `time` | str                                       | 时间限制(格式: RFC3339)<br/>例如：2022-01-01T00:00:00Z | 无        |
| `operator`    | Literal['<', '>', '<=', '>=', '==', '!='] | 大小比较运算符                                         | `>=`      |

## :recycle: 示例

### 筛选 txt 和 md 文件

```yaml
flow:
  steps:
    # 扫描 archive 目录
    - name: scan
      dir: archive

    # 筛选 txt 和 md 文件，保存至 txt_context 和 md_context 上下文
    # 未满足条件的文件保存至 not_match_context 上下文
    - name: switch
      default_key: not_match_context
      cases:
        - mode: glob
          includes:
            - '*.txt'
          save_key: txt_context

        - mode: glob
          includes:
            - '*.md'
          save_key: md_context

    # 打印 txt_context 上下文的文件列表
    - name: log
      load_key: txt_context
      file_name: txt_files

    # 打印 md_context 上下文的文件列表
    - name: log
      load_key: md_context
      file_name: md_files

    # 打印 not_match_context 上下文的文件列表
    - name: log
      load_key: not_match_context
      file_name: not_match_files
```

### 筛选大于 1MB 的文件

```yaml
flow:
  steps:
    # 扫描 archive 目录
    - name: scan
      dir: archive

    # 筛选大于 1MB 的文件，保存至 big_context 上下文
    # 未满足条件的文件保存至 not_match_context 上下文
    - name: switch
      default_key: not_match_context
      cases:
        - mode: size
          size: 1.0
          unit: mb
          save_key: big_context

    # 打印 big_context 上下文的文件列表
    - name: log
      load_key: big_context
      file_name: big_files

    # 打印 not_match_context 上下文的文件列表
    - name: log
      load_key: not_match_context
      file_name: not_match_files
```