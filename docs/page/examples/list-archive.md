# 识别压缩包

!!! note "场景需求"

    识别 archive/base 文件夹中压缩包的类型。

## 处理流程

```yaml
flow:
  steps:
    # 扫描压缩包
    - name: scan
      dir: archive/base

    # 测试压缩包
    - name: archive
      # 识别模式
      mode: list
      # 识别统计信息 info/list.json
      stat_file_name: list
```
