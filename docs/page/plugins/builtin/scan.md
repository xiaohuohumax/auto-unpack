---
icon: material/magnify-scan
---

# Scan

!!! info "Scan 插件"

    Scan 插件用于扫描指定目录下的文件，将符合条件的文件保存至上下文以供后续步骤使用。

## :link: 上下文

| 上下文     | 类型 | 描述             | 默认值      |
| ---------- | ---- | ---------------- | ----------- |
| `save_key` | str  | 扫描到的文件列表 | `'default'` |

## :gear: 配置

### ScanPluginConfig

!!! info "ScanPluginConfig"

    `auto_unpack.plugins.scan.ScanPluginConfig`

| 名称                      | 类型            | 描述                            | 默认值     |
| ------------------------- | --------------- | ------------------------------- | ---------- |
| :star: `name`             | Literal['scan'] | 插件名称，固定为 `'scan'`       | `'scan'`   |
| :star: `dir`              | Path            | 扫描目录                        | 无         |
| `includes`                | List[str]       | 包含的文件路径列表，glob 表达式 | `['**/*']` |
| `excludes`                | List[str]       | 排除的文件路径列表，glob 表达式 | `[]`       |
| `include_dir`             | bool            | 是否包含文件夹                  | `false`    |
| `deep`                    | bool            | 是否递归扫描子目录              | `true`     |
| [`上下文字段见上文`](#_1) |                 |                                 |            |

## :recycle: 示例

### 扫描文件夹 archive 下所有 zip 文件

```yaml
flow:
  steps:
    # 扫描 output 文件夹下所有 zip 文件
    - name: scan
      dir: archive
      includes:
        - "*.zip"

    # 打印扫描到的文件
    - name: log
      file_name: zip_files
```
