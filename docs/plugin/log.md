# Log

Log 插件用于打印上下文中的文件信息。

## 上下文

- `load_key`：要处理的文件列表，默认值为 `default`。

## 配置

```yaml
flow:
  steps:
    # 使用 log 插件
    - name: log
      # 需要打印的上下文
      # load_key: default

      # 打印文件名
      file_name: log
```

## 示例

### 打印文件夹 `archive` 下所有文件

```yaml
flow:
  steps:
    - name: scan
      dir: archive
    - name: log
      file_name: log
```