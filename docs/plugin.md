# 插件介绍

## 插件分类

### 1. 流程控制, 循环类插件

+ [X] [filter](../auto_unpack/plugin/control/filter.py) 筛选
+ [X] [loop](../auto_unpack/plugin/control/loop.py) 循环
+ [X] [merge](../auto_unpack/plugin/control/merge.py) 合并
+ [X] [switch](../auto_unpack/plugin/control/switch.py) 条件分支

### 2. 处理类插件

+ [x] [archive](../auto_unpack/plugin/archive.py) 压缩包处理
+ [x] [empty](../auto_unpack/plugin/empty.py) 删除空文件夹
+ [x] [log](../auto_unpack/plugin/log.py) 日志记录
+ [x] [remove](../auto_unpack/plugin/remove.py) 删除文件
+ [x] [rename](../auto_unpack/plugin/rename.py) 文件重命名
+ [x] [scan](../auto_unpack/plugin/scan.py) 扫描文件
+ [x] [transfer](../auto_unpack/plugin/transfer.py) 移动文件
+ [x] [flat](../auto_unpack/plugin/flat.py) 扁平化文件夹

## 插件上下文

插件的上下文指的是: 各个插件间共享的文件信息。

例如：

- `scan` 插件扫描文件夹，将扫描到符合需求的结果保存到上下文中(save_key)，供后续插件使用。
- `archive` 插件从上下文中(load_key)获取文件信息，将符合条件的压缩包进行解压缩。
- `remove` 则是对上下文中(load_key)获取的文件加工后再存入上下文中(save_key)，供后续插件使用。