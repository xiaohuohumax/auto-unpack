# 解压嵌套压缩包

!!! note "场景介绍"

    扫描路径 archive/loop 下所有嵌套压缩包，解压输出到目录 output。
    


## 处理流程

```yaml
# 解压嵌套压缩包流程
# 注意: 循环流程请谨慎使用, 防止死循环

flow:
  steps:
    # 将压缩包拷贝到output目录
    - name: scan
      dir: archive/loop
    - name: transfer
      mode: copy
      keep_structure: false
      target_dir: output

    # 循环处理output目录下的文件
    - name: scan
      dir: output
    # 循环结束条件:
    # 上下文中文件数量为0时结束循环
    - name: loop
      # 最大循环次数, 防止意外死循环
      max_loops: 10
      # 执行步骤 同: flow.steps 一样
      steps:
        # 解压文件
        - name: archive
          mode: extract
          target_dir: output
          stat_file_name: extract

        # 删除解压成功的文件
        # 这里需要将已经解压的文件移到其他目录/删除
        # 防止循环中重复解压
        - name: remove

        # 清理空文件夹
        - name: empty
          dir: output

        # 再次重新扫描output目录, 并识别是否有新的压缩包
        - name: scan
          dir: output
        - name: archive
          mode: list

```
