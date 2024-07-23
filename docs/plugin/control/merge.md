# Merge

Merge 插件用于合并多个上下文中的文件列表，并保存到新的上下文中。

## 上下文

- `save_key`：合并后的文件列表，默认值为 `default`。
- `context_keys`：需要合并的文件列表。

## 配置

```yaml
flow:
  steps:
    # 使用 merge 插件
    - name: merge
      # save_key: ...
      context_keys:
        - key1
        - key2
```

## 示例

### 将扫描到的 txt 和 md 文件合并到 `default` 上下文中。

```yaml
flow:
  steps:
    # 扫描 txt 文件，保存到 txt_context 上下文
    - name: scan
      dir: archive
      includes:
        - '*.txt'
      save_key: txt_context

    # 日志打印 txt_context 上下文内容
    - name: log
      load_key: txt_context
      file_name: txt_files

    # 扫描 md 文件，保存到 md_context 上下文
    - name: scan
      dir: archive
      includes:
        - '*.md'
      save_key: md_context

    # 日志打印 md_context 上下文内容
    - name: log
      load_key: md_context
      file_name: md_files

    # 使用 merge 插件合并两个上下文到默认（default）上下文
    - name: merge
      # save_key: ...
      context_keys:
        - txt_context
        - md_context

    # 日志打印合并后的上下文内容
    - name: log
      file_name: merged
```