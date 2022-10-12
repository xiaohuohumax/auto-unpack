<p align="center"><img src="img/logo.png"></p>

## 功能作用

批量识别压缩包的类型,测试其完整性,并通过密码表解压到指定位置

**简而言之**:批量解压压缩包

## 如何使用

1. 克隆 auto-unpack 源码到本地,并解压
2. 安装 python3 环境[已安装则可忽略]
3. 根据自身需求修改配置文件 [config.yaml](./config.yaml)
4. 将所有待解压压缩包放入 [pack](./pack) 文件夹
5. 所有密码填入密码表 [passwords.txt](./passwords.txt) **注意**:密码表一行一个密码
6. 运行脚本 [main.bat](./main.bat) 或者运行 python main.py
7. 等待脚本执行完成,解压后的文件存放于 [unpack](./unpack) 文件夹

## 实现说明

通过调用 7zip.exe 实现批量解压压缩包

## 执行流程

1. 从待解压文件夹中筛选符合要求的待解压文件
2. 测试待解压文件的完整性,顺便匹配密码,文件不完整或者没匹配中密码的则视为测试失败
3. 解压测试成功的待解压文件

## 目录说明

```text
auto-unpack
 ├── banner
 ├── config.py
 ├── config.yaml            / 配置
 ├── exception.py
 ├── img
 │   └── logo.png
 ├── log.py
 ├── main.bat               / 命令行启动脚本
 ├── main.py                / 程序入口
 ├── pack                   / 待解压文件存放文件夹
 ├── passwords.txt          / 密码表
 ├── readme.md
 ├── unpack                 / 解压完成存放文件夹
 ├── unpack.log
 ├── unpack_report.txt      / 自动解压完成结果统计
 ├── util7zip               / 7-zip 依赖
 │   ├── lib7zip
 │   │   ├── 7-zip.chm      / command chm
 │   │   ├── 7-zip.chw
 │   │   ├── 7z.dll
 │   │   ├── 7z.exe         / 7-zip
 │   │   ├── History.txt
 │   │   ├── License.txt
 │   │   └── readme.txt
 │   └── util_7z.py         / 7-zip 简单包装
 └── utils.py
```

## 其他

[7-zip官网链接](https://7-zip.org/)
