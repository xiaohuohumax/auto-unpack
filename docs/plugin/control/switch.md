# Switch

Switch 插件用于根据条件分支筛选上下文的文件列表，满足条件的文件列表将保存至对应的上下文，未满足条件的文件列表将保存至 `default_key` 上下文。

## 上下文

- `load_key`：要分支的文件列表，默认值为 `default`。
- `default_key`：未满足条件的文件列表。
- `cases[].save_key`：满足条件的文件列表。

## 配置

```yaml
flow:
  steps:
    # 使用 switch 插件
    - name: switch
      # load_key: ...
      # default_key: ...
      # 分支条件
      cases: []
```

## 分支条件

### 通过文件大小筛选

```yaml
flow:
  steps:
    - name: switch
      cases:
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
          # 保存至 md_context 上下文
          save_key: md_context
```

### 通过文件路径筛选

```yaml
flow:
  steps:
    - name: switch
      cases:
        - mode: glob
          # context => includes => excludes => True(保存至 save_key 上下文) False(后续条件判断)
          # 包含
          includes:
            - '*.md'
          # 排除
          excludes:
            - 'README.md'
          # 保存至 md_context 上下文
          save_key: md_context
```

## 示例

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