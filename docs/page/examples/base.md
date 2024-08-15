# 解压普通压缩包

!!! note "场景介绍"

    扫描路径 archive/base 下所有压缩包，解压输出到目录 output，并将解压信息保存至 info/extract.json。
    


## 处理流程

```yaml
# 解压普通压缩包流程

flow:
  steps:
    # 扫描压缩包
    - name: scan
      # 扫描路径
      dir: archive/base

    # 解压压缩包
    - name: archive
      # 解压模式
      mode: extract
      # 压缩文件保存目录
      output_dir: output
      # 解压统计信息 info/extract.json
      stat_file_name: extract

```
