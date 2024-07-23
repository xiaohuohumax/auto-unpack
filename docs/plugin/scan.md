# Scan

Scan 插件用于扫描指定目录下的文件，将符合条件的文件保存至上下文以供后续步骤使用。

## 上下文

- `save_key`：改名后的文件列表，默认值为 `default`。

## 配置

```yaml
flow:
  steps:
    # 使用 scan 插件
    - name: scan
      # save_key: default

      # 扫描路径
      dir: archive

      # 包含/排除的文件类型，glob 语法
      # file_path => includes => excludes => True(保留) False(排除)
      includes:
        - "*.zip"
      excludes:
        - "*.txt"

      # 是否包含文件夹，默认 false
      # include_dir: false
```

## 示例

### 扫描文件夹 `archive` 下所有 `zip` 文件。

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
