<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/xiaohuohumax/auto-unpack/main/logo.png">
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/xiaohuohumax/auto-unpack/main/logo-dark.png">
    <img alt="logo" src="https://raw.githubusercontent.com/xiaohuohumax/auto-unpack/main/logo.png">
  </picture>
</p>

**压缩包自动解压工具，支持多种压缩包格式。通过组合各种插件，编排流程，则可满足日常解压需求。**

## 🎯 使用场景

+ 场景一：当压缩包格式不确定，种类繁多，且已经知道密码时。
+ 场景二：当压缩包存放位置分散，解压完成后需要移动到指定位置时。
+ 场景三：当解压后的文件需要分类整理时。
+ 场景四：当解压后的文件需要删除指定文件时。

**总之，通过组合各种插件，设计出适合自己的解压流程。**

## ⚙️ 安装

```shell
pip install auto-unpack
```

## 🖥️ 使用

创建项目文件夹大致结构如下：

```txt
project
 ├── banner.txt                     // 程序启动banner【可选】
 ├── .env                           // 环境变量文件
 ├── config
 │   ├── application[.mode].yaml    // 应用配置（不同模式）
 │   ├── application.yaml           // 应用配置
 │   └── logging.yaml               // 日志配置【可选】
 ├── main.py                        // 入口文件
 └── passwords.txt                  // 密码表
```

logging.yaml 配置参考：[config/logging.yaml](https://github.com/xiaohuohumax/auto-unpack/blob/main/config/logging.yaml)

application.yaml 配置参考：

- [config/application.yaml](https://github.com/xiaohuohumax/auto-unpack/blob/main/config/application.yaml)
- [config/application.base.yaml](https://github.com/xiaohuohumax/auto-unpack/blob/main/config/application.base.yaml)

.env 环境变量：

```txt
# 运行模式，对应配置文件中的 application[.mode].yaml
MODE=local
# 配置文件目录 => config
config_dir=config
```
main.py 代码：

```python
from auto_unpack import App

app = App()

if __name__ == '__main__':
    app.run()
```

最后，运行 `python main.py [--mode=local]` 即可启动程序。

## 🚨 注意事项

+ 新流程请先小范围测试，确保功能正常，防止压缩包处理意外造成数据丢失或损坏。

## 📚 支持格式

+ **压缩/解压缩**:
  7z、XZ、BZIP2、GZIP、TAR、ZIP 以及 WIM
+ **仅解压缩**:
  AR、ARJ、CAB、CHM、CPIO、CramFS、DMG、EXT、FAT、GPT、HFS、IHEX、ISO、LZH、LZMA、MBR、MSI、NSIS、NTFS、QCOW2、RAR、RPM、SquashFS、UDF、UEFI、VDI、VHD、VMDK、WIM、XAR
  以及 Z

## 🔗 相关链接

+ [Rye](https://rye.astral.sh/)
+ [7-zip](https://7-zip.org/)