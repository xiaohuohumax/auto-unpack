# 🌳 项目结构

```
auto-unpack
 ├── archive                // 压缩包存放目录
 ├── auto-unpack.exe        // WinSW 服务主程序
 ├── auto-unpack.xml        // WinSW 配置文件
 ├── auto_unpack
 │   ├── app.py             // 程序主入口
 │   ├── args.py            // 命令行参数解析
 │   ├── config.py          // 配置文件解析
 │   ├── env.py             // 环境变量解析
 │   ├── plugin             // 插件目录
 │   ├── plugin.py          // 插件管理
 │   ├── store.py           // 数据仓库(插件上下文)
 │   └── util               // 工具库目录
 │       ├── config.py
 │       ├── file.py
 │       ├── lib            // 第三方库7-zip目录
 │       │   ├── 7-zip.chm
 │       │   ├── 7-zip.chw
 │       │   ├── History.txt
 │       │   ├── License.txt
 │       │   ├── readme.txt
 │       │   └── win
 │       ├── logging.py      // 日志配置
 │       └── sevenzip.py     // 7-zip 工具封装
 ├── banner.txt
 ├── config                  // 配置文件目录
 │   ├── application[.test].yaml    // 对应模式的配置文件
 │   ├── application.yaml           // 程序配置
 │   └── logging.yaml               // 日志配置
 ├── info                   // 流程执行期间产生的信息
 ├── job.py                 // 解压做成任务
 ├── LICENSE
 ├── log                    // 日志目录
 ├── logo-dark.png
 ├── logo.png
 ├── main.py                // 程序入口
 ├── output                 // 解压输出目录
 ├── passwords.txt          // 密码表
 ├── pyproject.toml         // 项目依赖管理文件
 ├── README.md
 ├── requirements-dev.lock  // 开发环境依赖
 └── requirements.lock      // 运行环境依赖
```