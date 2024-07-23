# Flat

Flat 插件用于扁平化文件结构，即将所有文件移动根目录下。

## 上下文

- 无

## 配置

```yaml
flow:
  steps:
    # 使用 flat 插件
    - name: flat
      # 需要扁平化的文件夹
      dir: output

      # 扁平化的深度, 空则表示不限制深度
      # 例如：depth=1 表示只扁平化第一层文件夹
      # depth: 1
```

## 示例

### 将文件夹 `output` 中的所有文件移动到根目录下

```txt
output/
├── file1.txt
├── file2.txt
└── subfolder/
    ├── file3.txt
    └── file4.txt

# flat 后

output/
├── file1.txt
├── file2.txt
├── file3.txt
├── file4.txt
└── subfolder/

```

```yaml
flow:
  steps:
    # 使用 flat 插件
    - name: flat
      dir: output
```