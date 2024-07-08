<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="logo.png">
    <source media="(prefers-color-scheme: light)" srcset="logo-dark.png">
    <img alt="logo" src="logo.png">
  </picture>
</p>

**压缩包自动解压工具，支持多种压缩包格式。通过组合各种插件，编排流程，则可满足日常解压需求。**

## 🎯 使用场景

+ 场景一：当压缩包格式不确定，种类繁多，且已经知道密码时。
+ 场景二：当压缩包存放位置分散，解压完成后需要移动到指定位置时。
+ 场景三：当解压后的文件需要分类整理时。
+ 场景四：当解压后的文件需要删除指定文件时。

**总之，通过组合各种插件，设计出适合自己的解压流程。**

## 🔨 现有插件

[插件介绍](./docs/plugin.md)

## 📖 使用说明

### 1. 下载源码

```shell
git clone https://github.com/xiaohuohumax/auto-unpack.git
```

### 2. 安装依赖

```shell
rye sync
# 或
pip3 install -r requirements.lock -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 3. 编写流程

参考：[config/application[.mode].yaml](./config) 配置文件的 `flow` 流程配置。

### 4. 运行工具

```shell
rye run start

# 不同模式
rye run start -m [mode]
# 例如：rye run start -m test => config/application.test.yaml

# 定时任务
rye run job
```

Windows 也可搭配 [WinSW](https://github.com/winsw/winsw) 工具，将 auto-unpack 做成系统服务。

参考：[auto-unpack.xml](./auto-unpack.xml)

```shell
# 安装服务
auto-unpack.exe install
# 启动服务
auto-unpack.exe start
# 停止服务
auto-unpack.exe stop
# 卸载服务
auto-unpack.exe uninstall
```

## 🚨 注意事项

+ 新流程请先小范围测试，确保功能正常，防止压缩包处理意外造成数据丢失或损坏。

## 🚧 后续计划

+ [ ] 适配 Linux/Mac 环境

## 🌳 项目结构

[项目结构](./docs/tree.md)


## 📚 支持格式


+ **压缩/解压缩**:
  7z、XZ、BZIP2、GZIP、TAR、ZIP 以及 WIM
+ **仅解压缩**:
  AR、ARJ、CAB、CHM、CPIO、CramFS、DMG、EXT、FAT、GPT、HFS、IHEX、ISO、LZH、LZMA、MBR、MSI、NSIS、NTFS、QCOW2、RAR、RPM、SquashFS、UDF、UEFI、VDI、VHD、VMDK、WIM、XAR
  以及 Z

## 🔗 相关链接

+ [Rye](https://rye.astral.sh/)
+ [7-zip](https://7-zip.org/)