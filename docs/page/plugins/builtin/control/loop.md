---
icon: material/sync
---

# Loop

!!! info "Loop 插件"
    
    Loop 插件用于循环执行流程，直到条件不满足为止（即上下文中的文件列表为空时结束循环）。

## :link: 上下文

| 上下文     | 类型 | 描述                 | 默认值      |
| ---------- | ---- | -------------------- | ----------- |
| `load_key` | str  | 要循环处理的文件列表 | `'default'` |

## :gear: 配置

### LoopPluginConfig


!!! info "LoopPluginConfig"

    `auto_unpack.plugins.control.loop.LoopPluginConfig`

| 名称                      | 类型            | 描述                                     | 默认值   |
| ------------------------- | --------------- | ---------------------------------------- | -------- |
| :star: `name`             | Literal['loop'] | 插件名称，固定为 `'loop'`                | `'loop'` |
| `steps`                   | List[Any]       | 需要循环执行的步骤，同 `flow.steps` 一样 | `[]`     |
| `max_loops`               | int             | 最大循环次数，-1：不限制                 | `1024`   |
| `loop_interval`           | int             | 循环间隔时间，单位：秒                   | `1`      |
| [`上下文字段见上文`](#_1) |                 |                                          |          |

## :recycle: 示例

### 解压嵌套压缩的文件

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