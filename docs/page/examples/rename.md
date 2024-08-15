# 文件重命名

!!! note "场景介绍"

    部分分卷压缩的压缩包，文件名中会包含多余的文字，需要重命名才能正确解压。
    
!!! tip "例如"

    `改名前`：icon-v.7z.001, icon-v.7z.002删除, icon-v.7z.003删除<br/>
    `改名后`：icon-v.7z.001, icon-v.7z.002, icon-v.7z.003

## 处理流程

```yaml
# 文件重命名流程

flow:
  steps:
    # 复制压缩包到输出目录
    - name: scan
      dir: archive/rename
    - name: transfer
      mode: copy
      target_dir: output/rename

    # 扫描并重命名压缩包
    - name: scan
      dir: output/rename
    - name: rename
      rules:
        - mode: replace
          replace: ""
          search: 删除

    # 解压压缩包
    - name: archive
      # 解压模式
      mode: extract
      # 压缩文件保存目录
      output_dir: output
      # 解压统计信息 info/extract.json
      stat_file_name: extract

```
