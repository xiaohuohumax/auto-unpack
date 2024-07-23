# Filter

Filter 插件依照配置过滤筛选上下文中的文件列表，并将符合条件的文件列表保存到上下文以供后续步骤使用。

## 上下文

- `load_key`：要过滤的文件列表，默认值为 `default`。
- `save_key`：过滤后的文件列表，默认值为 `default`。
- `exclude_key`：过滤后需要排除的文件列表。

## 配置

```yaml
flow:
  steps:
    # 使用 filter 插件
    - name: filter
      # load_key: ...
      # save_key: ...
      # exclude_key: ...
      # 过滤规则
      rules: []
```

## 过滤规则

过滤规则是一个列表，满足全部规则的文件才会被保留。

### 通过文件大小过滤

```yaml
- name: filter
  rules:
    - mode: size
      # file_size operator size * unit => True(保留) False(过滤)

      # 文件大小，浮点数
      size: 10.0
      # 运算符，可选：>, >=, <, <=, ==, !=
      # 默认为 >=
      operator: '>='
      # 单位，可选：b, kb, mb, gb, tb
      # 默认为 mb
      unit: mb
```

### 通过文件路径过滤

```yaml
- name: filter
  rules:
    - mode: glob
      # file_path => includes => excludes => True(保留) False(过滤)

      # glob 规则
      # 包含的文件路径列表
      includes:
        - '*.txt'
        - '*.md'
      # 排除的文件路径列表
      excludes:
        - 'README.md'
```

## 示例

### 保留文件大小 大于等于 1MB 的 txt 和 md 文件，并排除名叫 README.md 文件。

```yaml
flow:
  steps:
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