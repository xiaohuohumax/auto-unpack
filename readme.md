<p style="text-align:center;"><img src="./img/logo.png" alt="auto-unpack"></p>

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

通过调用 7z.exe 实现批量解压压缩包

## 执行流程

**流程说明**: 流程[2-7]可开启/关闭,可以灵活配置

1. 压缩包扫描: 扫描待解压文件夹下全部文件(是否包含子文件夹)
2. 压缩包改名: 批量将异常分卷压缩包改回正确后缀 例如: .part01删除.rar -> .part01.rar
3. 压缩包过滤: 筛选压缩包文件,排除不想解压的文件
4. 压缩包识别: 识别压缩包的信息,是否分卷压缩,压缩类型,大小等等
5. 压缩包测试: 测试压缩包完整性,并尝试匹配密码表的密码
6. 压缩包解压: 解压压缩包
7. 压缩包清理: 清理空文件夹
8. 生成执行报告

## 状态说明

```text
# 此文件已被收录准备执行后续操作
SCAN = '扫描收录'

RENAME = '修改名字'
RENAME_FAIL = '改名失败'
UN_RENAME = '未改名字'

# 可以进行后续识别,测试,解压操作
FILTER_INCLUDE = '过滤包含'

FILTER_EXCLUDE = '过滤排除'

# 压缩包信息识别成功
ANALYSIS_SUCCESS = '识别成功'

# 压缩信息识别失败 (注意: 某些类型压缩包需要输入密码才可识别,若密码错误也会识别失败)
ANALYSIS_FAIL = '识别失败'

# 识别成功 且被识别为分卷压缩的子卷 (注意: 某些类型子卷无法识别 例如:7z.002 则会被设置为 识别失败 'ANALYSIS_FAIL')
ANALYSIS_SUCCESS_SPLIT = '识别成功(分卷子卷)'

# 测试 (只会测试 识别成功的压缩包,子卷排除)
# 测试成功(压缩包完整)
TEST_SUCCESS = '测试成功'

TEST_FAIL = '测试失败'

# 解压操作
UNPACK_SUCCESS = '解压成功'

UNPACK_FAIL = '解压失败'
```

## 目录说明

```text
auto-unpack
 ├── banner
 ├── clear.bat
 ├── config.py              // 配置类
 ├── config.yaml            // *全局配置
 ├── core.py
 ├── img
 │   └── logo.png
 ├── LICENSE
 ├── log.py                 // 日志配置类
 ├── main.bat               // *cmd快捷运行
 ├── main.py                // *项目入口
 ├── pack                   // *压缩包存放文件夹
 │   └── hello world 7z     // 测试压缩包 7z 类型 密码:auto-unpack
 ├── passwords.txt          // *密码表
 ├── readme.md
 ├── report.txt             // 执行后的统计报告
 ├── unpack                 // *压缩包解压后存放文件夹
 ├── unpack.log
 ├── util7zip               // 7-zip 命令行调用库
 │   ├── lib7zip
 │   │   ├── 7-zip.chm      // 7z.exe 命令手册
 │   │   ├── 7-zip.chw
 │   │   ├── 7z.dll
 │   │   ├── 7z.exe
 │   │   ├── History.txt
 │   │   ├── License.txt
 │   │   └── readme.txt
 │   ├── result.py
 │   ├── utils.py
 │   ├── util7z.py          // 库主文件
 │   └── __init__.py
 └── utils.py
```

## 7-zip支持格式

+ **压缩/解压缩**:
  7z、XZ、BZIP2、GZIP、TAR、ZIP 以及 WIM
+ **仅解压缩**:
  AR、ARJ、CAB、CHM、CPIO、CramFS、DMG、EXT、FAT、GPT、HFS、IHEX、ISO、LZH、LZMA、MBR、MSI、NSIS、NTFS、QCOW2、RAR、RPM、SquashFS、UDF、UEFI、VDI、VHD、VMDK、WIM、XAR
  以及 Z

## 其他

[7-zip官网链接](https://7-zip.org/)
