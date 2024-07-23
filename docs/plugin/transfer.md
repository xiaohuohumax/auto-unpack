# Transfer

Transfer 插件用于移动上下文中的文件列表。

## 上下文

- `load_key`：要移动的文件列表，默认值为 `default`。
- `save_key`：移动后的文件列表，默认值为 `default`。

## 配置

```yaml
flow:
  steps:
    # 使用 transfer 插件
    - name: transfer
      # load_key: default
      # save_key: default

      # 移动模式
      # 可选：move（移动）, copy（复制）
      mode: move

      # 目标路径
      target_dir: output

      # 是否保留原文件结构，默认：true
      # keep_structure: true

      # 覆盖模式，默认：rename
      # 可选：rename（重命名）, skip（跳过）, overwrite（覆盖）
      # overwrite_mode: rename
```

## 示例

### 将文件夹 `archive` 中的所有文件复制到 `output` 文件夹下

```yaml
flow:
  steps:
    # 扫描 archive 文件夹
    - name: scan
      dir: archive

    # 将扫描的文件复制到 output 文件夹下
    - name: transfer
      mode: copy
      target_dir: output
```