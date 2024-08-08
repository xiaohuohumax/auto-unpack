# 🌳 项目结构

```txt
auto-unpack
 ├── auto_unpack
 │   ├── app.py             // 程序主入口
 │   ├── args.py            // 命令行参数解析
 │   ├── config.py          // 配置文件解析
 │   ├── constant.py        // 常量定义
 │   ├── env.py             // 环境变量解析
 │   ├── store.py           // 数据仓库(插件上下文)
 │   ├── plugin.py          // 插件管理
 │   ├── plugins            // 内置插件目录
 │   └── util                       // 工具库目录
 │       ├── config.py
 │       ├── file.py
 │       ├── exec.py
 │       ├── logging.py
 │       └── sevenzip               // 7zip工具包
 │           ├── result.py
 │           └── lib                // 7zip库文件
 │               ├── darwin         // MacOS
 │               ├── linux          // Linux
 │               ├── windows        // Windows
 │               ├── 7-zip.chm
 │               ├── 7-zip.chw
 │               ├── History.txt
 │               ├── License.txt
 │               └── readme.txt
 ├── archive                        // 压缩包存放目录
 ├── config                         // 配置文件目录
 │   ├── application.[test].yaml    // 对应模式的配置文件
 │   ├── application.yaml           // 程序配置
 │   └── logging.yaml               // 日志配置
 ├── docs                           // 文档目录
 ├── info                           // 流程执行期间产生的信息
 ├── log                            // 日志目录
 ├── output                         // 解压输出目录
 ├── schema                             // schema目录
 │   ├── [version]                      // 对应版本目录
 │   ├── auto-unpack-flow-schema.json   // 最新版流程schema
 │   └── auto-unpack-schema.json        // 最新版配置schema
 ├── .env               // 环境变量文件
 ├── auto-unpack.exe    // WinSW 服务主程序
 ├── auto-unpack.xml    // WinSW 配置文件
 ├── banner.txt
 ├── job.py             // 定时任务
 ├── LICENSE
 ├── logo-dark.png
 ├── logo.png
 ├── main.py            // 程序入口
 ├── mkdocs.yml         // 文档配置文件
 ├── passwords.txt      // 密码表
 ├── PYPI_README.md
 ├── pyproject.toml
 ├── README.md
 ├── requirements-dev.lock  // 开发环境依赖
 ├── requirements.lock      // 运行环境依赖
 └── schema.py              // schema生成工具
```