# background service template

这是一个 auto-unpack 的后台服务模板。

> [!NOTE]
> 将项目部署为服务后台运行，实现自动定时解压功能。

## 📖 使用文档

+ 文档：[https://xiaohuohumax.github.io/auto-unpack/](https://xiaohuohumax.github.io/auto-unpack/)
+ PyPI：[https://pypi.org/project/auto-unpack/](https://pypi.org/project/auto-unpack/)

## 🛠️ 安装依赖

```bash
rye sync
# 或者
pip3 install -r requirements.lock
```

## 🚀 运行项目

```bash
rye run job
# 或者
python -m app.job
```

## 🔧 注册服务

> [!WARNING] 注意
> WinSW 只适用于 Windows 系统。

配置文件：auto-unpack.xml，参考：[WinSW](https://github.com/winsw/winsw)

```bash
# 注册服务
auto-unpack.exe install
# 启动服务
auto-unpack.exe start
# 停止服务
auto-unpack.exe stop
# 卸载服务
auto-unpack.exe uninstall
```