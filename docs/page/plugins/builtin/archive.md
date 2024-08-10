---
icon: material/folder-zip-outline
---

# Archive

!!! info "Archive 插件"

    Archive 插件用于处理压缩包文件，包括识别、测试、解压等操作。

## :link: 上下文

| 上下文     | 类型 | 描述               | 默认值      |
| ---------- | ---- | ------------------ | ----------- |
| `load_key` | str  | 要处理的文件列表   | `'default'` |
| `save_key` | str  | 处理成功的文件列表 | `'default'` |
| `fail_key` | str  | 处理失败的文件列表 | 无          |

## :gear: 配置

### ArchivePluginConfig

!!! info "ArchivePluginConfig"

    `auto_unpack.plugins.archive.ArchivePluginConfig`

| 名称                                | 类型                               | 描述                                                                                                                                      | 默认值            |
| ----------------------------------- | ---------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- | ----------------- |
| :star: `name`                       | Literal['archive']                 | 插件名称，固定为 `'archive'`                                                                                                              | `'archive'`       |
| :star: `mode`                       | Literal['list', 'extract', 'test'] | 压缩包处理模式<br/>`list`: 列出压缩包内文件信息<br/>`extract`: 解压压缩包<br/>`test`: 测试压缩包完整性                                    | `'extract'`       |
| `password_path`                     | Path                               | 密码表文件路径 [密码表规则](#_3)                                                                                                          | `'passwords.txt'` |
| `stat_file_name`                    | Optional[str]                      | 统计信息文件名，不同模式对应不同统计信息                                                                                                  | 无                |
| `thread_max`                        | int                                | 线程池最大线程数                                                                                                                          | 10                |
| `result_processing_mode`            | Literal['strict', 'greedy']        | 结果处理模式<br/>`strict`：严格模式，结果绝对依靠 7-zip 命令行输出<br/>`greedy`：贪婪模式，7-zip 返回某些错误码时，也会尝试识别/测试/解压 | `'strict'`        |
| `output_dir`<br/>`mode=extract可用` | Path                               | 压缩包存放目录                                                                                                                            | `'output'`        |
| `keep_dir`<br/>`mode=extract可用`   | bool                               | 是否保持解压后的文件夹结构                                                                                                                | `true`            |
| [`上下文字段见上文`](#_1)           |                                    |                                                                                                                                           |                   |

## 密码表规则

1. 密码一行一个
2. 空行不使用
3. 密码越靠前的越先尝试
4. 第一条分割线后为密码

例如：

```txt
第一条分割线前面是注释
----------------------------------------
123456
abc123
...
```

## :recycle: 示例

### 解压 文件夹 archive 下所有 zip 类型的压缩包到 output 目录

```yaml
flow:
  steps:
    # 扫描压缩包文件
    - name: scan
      dir: archive
      includes:
        - "*.zip"

    # 解压压缩包
    - name: archive
      mode: extract
      output_dir: output
      # 解压结果统计
      stat_file_name: stat
```

### 识别文件夹 archive 下的所有压缩包

```yaml
flow:
  steps:
    # 扫描压缩包文件
    - name: scan
      dir: archive

    # 识别压缩包
    - name: archive
      mode: list
      # 识别结果统计
      stat_file_name: stat
```

### 将文件夹 archive 下的所有压缩包复制到 output 目录

```yaml
flow:
  steps:
    # 扫描压缩包文件
    - name: scan
      dir: archive

    # 识别压缩包
    - name: archive
      mode: list
      # 识别结果统计
      stat_file_name: stat

    # 复制识别成功的压缩包到 output 目录
    - name: transfer
      mode: copy
      target_dir: output
```

### 测试文件夹 archive 下的所有压缩包

```yaml
flow:
  steps:
    # 扫描压缩包文件
    - name: scan
      dir: archive

    # 测试压缩包
    - name: archive
      mode: test
      # 测试结果统计
      stat_file_name: stat
```