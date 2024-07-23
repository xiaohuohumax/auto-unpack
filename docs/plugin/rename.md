# Rename

Rename 插件用于修改上下文中的文件的名称。

## 上下文

- `load_key`：要改名的文件列表，默认值为 `default`。
- `save_key`：改名后的文件列表，默认值为 `default`。

## 配置

```yaml
flow:
  steps:
    # 使用 rename 插件
    - name: rename
      # load_key: default
      # save_key: default

      # 改名规则链
      rules: []
```

## 改名规则链

### 替换改名

```yaml
flow:
  steps:
    - name: rename
      rules:
        # 替换模式
        - mode: replace
          # 匹配字符串
          search: old_word
          # 替换字符串
          replace: new_word
          # 替换次数，-1 表示全部替换
          # count: -1
```

### 正则改名

```yaml
flow:
  steps:
    - name: rename
      rules:
        # 正则模式
        - mode: re
          # 匹配正则表达式（可以使用捕获组）
          pattern: \d{4}
          # 替换字符串（捕获组使用 \1 表示）
          replace: ""
          # 替换次数，0 表示不替换
          # count: 0
          # 正则表达式匹配模式
          # flags: str = ''
```

## 示例

### 删除文件名中的 `删除` 字样

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