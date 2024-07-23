# Archive

Archive 插件用于处理压缩包文件，包括识别、测试、解压等操作。

## 上下文

- `load_key`：要处理的文件列表，默认值为 `default`。
- `save_key`：处理成功的文件列表，默认值为 `default`。
- `fail_key`：处理失败的文件列表。

## 配置

```yaml
flow:
  steps:
    # 使用 archive 插件
    - name: archive
      # 处理模式，可选：extract（解压）, list（识别）, test（测试）
      mode: extract

      # 密码表路径，默认为：passwords.txt
      # password_path: passwords.txt

      # 统计信息文件名，空表示不生成
      # stat_file_name: stat

      # 处理线程数，默认为 10
      # thread_max: 10

      # 不同模式存储对应数据
      # 比如：extract 模式下，save_key 对应解压成功的文件列表，fail_key 对应解压失败的文件列表
      # list 以及 test 模式同理
      # load_key: ...
      # save_key: ...
      # fail_key: ...

      # 结果处理模式，默认值为 strict
      # 可选：
      # strict：严格模式（结果绝对依靠 7-zip 命令行输出）
      # greedy：贪婪模式（7-zip 返回某些错误码时，也会尝试识别/测试/解压）
      # result_processing_mode: strict

      # 解压输出目录，默认值为 output
      # output_dir: output

      # 是否保留解压后的目录结构，默认值为 true
      # keep_dir: true
```

### 密码表规则

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

## 示例

### 解压 文件夹 `archive` 下所有 `zip` 类型的压缩包到 `output` 目录

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

### 识别文件夹 `archive` 下的所有压缩包

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

### 将文件夹 `archive` 下的所有压缩包复制到 `output` 目录

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

### 测试文件夹 `archive` 下的所有压缩包

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