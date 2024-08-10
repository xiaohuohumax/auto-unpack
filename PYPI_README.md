<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/xiaohuohumax/auto-unpack/main/logo.png">
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/xiaohuohumax/auto-unpack/main/logo-dark.png">
    <img alt="auto-unpack" src="https://raw.githubusercontent.com/xiaohuohumax/auto-unpack/main/logo.png">
  </picture>

  <div>
    <img alt="GitHub Actions Workflow Status" src="https://img.shields.io/github/actions/workflow/status/xiaohuohumax/auto-unpack/publish-package.yaml?label=Build">
    <img alt="GitHub Issues" src="https://img.shields.io/github/issues/xiaohuohumax/auto-unpack?label=Issues">
    <img alt="GitHub Pull Requests" src="https://img.shields.io/github/issues-pr/xiaohuohumax/auto-unpack?label=Pull%20Requests">
    <img alt="PyPI - License" src="https://img.shields.io/pypi/l/auto-unpack?label=License">
    <img alt="PyPI - Version" src="https://img.shields.io/pypi/v/auto-unpack?label=PyPi">
    <img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/auto-unpack?label=PyPi%20Downloads">
    <img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/xiaohuohumax/auto-unpack">
    <img alt="GitHub forks" src="https://img.shields.io/github/forks/xiaohuohumax/auto-unpack">
  </div>
</div>

# auto-unpack

**压缩包自动解压工具，支持多种压缩包格式。通过组合各种内置插件，编排解压流程，则可满足日常解压需求。**

## ⚡ 注意事项

+ 新流程请先测试，确保功能正常，防止压缩包处理意外造成重要数据丢失或损坏。
+ 项目处于开发阶段，使用时最好限定版本，避免因版本更新导致功能异常。
+ 欢迎提出宝贵建议[🚧](https://github.com/xiaohuohumax/auto-unpack/pulls)，反馈问题 [🐛](https://github.com/xiaohuohumax/auto-unpack/issues)。若觉得项目不错，欢迎 [⭐](https://github.com/xiaohuohumax/auto-unpack) 鼓励！

## 🎯 使用场景

+ 场景一：大量压缩包需要识别、测试、解压等。
+ 场景二：大量文件需要分类、重命名、移动、复制、删除等。
+ 场景三：需要定时、周期性处理文件。

## 📖 使用文档

+ 文档：[https://xiaohuohumax.github.io/auto-unpack/](https://xiaohuohumax.github.io/auto-unpack/)

## 📚 支持格式

+ **压缩/解压缩**：7z、XZ、BZIP2、GZIP、TAR、ZIP 以及 WIM
+ **仅解压缩**：AR、ARJ、CAB、CHM、CPIO、CramFS、DMG、EXT、FAT、GPT、HFS、IHEX、ISO、LZH、LZMA、MBR、MSI、NSIS、NTFS、QCOW2、RAR、RPM、SquashFS、UDF、UEFI、VDI、VHD、VMDK、WIM、XAR 以及 Z

## 🔗 相关链接

+ [Rye](https://rye.astral.sh/)：项目管理
+ [7-zip](https://7-zip.org/)：解压缩软件
