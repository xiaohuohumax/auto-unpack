# Remove

Remove 插件用于删除指定上下文的文件列表，删除后清空上下文。

## 上下文

- `load_key`：要删除的文件列表，默认值为 `default`。

## 配置

```yaml
flow:
  steps:
    # 使用 remove 插件
    - name: remove
      # 需要删除文件的上下文
      # load_key: default
```

## 示例

### 删除文件夹 `output` 下全部的 `txt` 文件

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