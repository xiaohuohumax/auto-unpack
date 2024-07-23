# Loop

Loop 插件用于循环执行流程，直到条件不满足为止（即上下文中的文件列表为空时结束循环）。

## 上下文

- `load_key`：要循环的文件列表，默认值为 `default`。

## 配置

```yaml
flow:
  steps:
    # 使用 loop 插件
    - name: loop
      # load_key: ...
      # 最大循环次数，默认值为 1024
      # max_loops: 1024
      # 循环间隔，单位为秒，默认值为 1
      # loop_interval: 1
      # 循环步骤
      steps: []
```

## 循环步骤

循环插件的 `steps` 字段用于配置循环步骤，循环步骤的配置与普通步骤（flow.steps）相同。

## 示例

### 解压嵌套压缩的文件。

| 路径     | 说明             |
| -------- | ---------------- |
| archive/ | 压缩文件存放路径 |
| output/  | 解压文件存放路径 |

```yaml
flow:
  steps:
    # 将压缩文件拷贝到 output 目录，并保存到上下文中
    - name: scan
      dir: archive
    - name: archive
      mode: list
    - name: transfer
      mode: copy
      target_dir: output

    # 循环结束条件:
    # 上下文中文件数量为0时结束循环
    - name: loop
      # 最大循环次数, 防止意外死循环
      max_loops: 10
      # 执行步骤 同: flow.steps 一样
      steps:

        # 解压上下文中的压缩文件，并将解压后的文件放到 output 目录
        - name: archive
          mode: extract
          target_dir: output
          stat_file_name: extract

        # 删除解压成功的压缩包
        # 这里需要将已经解压的文件移到其他目录/删除
        # 防止循环中重复解压
        - name: remove

        # 再次重新扫描 output 目录, 并识别是否有新的压缩包
        - name: scan
          dir: output
        # 过滤掉普通文件（也可通过文件大小筛选），减少识别压力
        - name: filter
          rules:
            - mode: glob
              excludes:
                - '*.txt'
                - '*.jpg'
        - name: archive
          mode: list

    # 循环结束后，清理 output 目录中的空文件夹
    - name: empty
      dir: output
```