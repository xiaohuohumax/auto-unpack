# Empty

Empty 插件用于删除指定目录下的所有空文件夹。

## 上下文

- 无

## 配置

```yaml
flow:
  steps:
    # 使用 empty 插件
    - name: empty
      # 需要清理空文件夹的目录
      dir: output
```

## 示例

### 清理文件夹 `output` 下的所有空文件夹

```yaml
flow:
  steps:
    - name: empty
      dir: output
```