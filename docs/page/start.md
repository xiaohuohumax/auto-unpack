---
hide:
  - navigation
---

# 快速开始

## 安装依赖

=== "Rye"

    ``` sh
    rye add auto-unpack
    ```

=== "Pypi"

    ``` sh
    pip install auto-unpack
    ```

## 初始项目

利用脚手架工具 `auto-unpack` 初始化项目

``` sh
# auto-unpack -h 查看帮助
auto-unpack init [project_path]
```

```
D:\Test\test>auto-unpack init .
[?] 请输入初始化项目目录: .
[?] 请选择模板:
 > 简单项目模板
   自定义插件模板
   后台服务模板

Initialized finished!

  cd .
  rye sync

```

## 运行项目

!!! warning "注意"

    模板使用 [Rye](https://rye.astral.sh/){target=_blank} 作为管理工具，若是不想使用 Rye，可使用以下命令运行项目：

    ```sh
    # 安装依赖
    pip install -r requirements.lock
    # 运行项目
    python -m app
    ```

```sh
cd .
# 安装依赖
rye sync
# 运行项目
rye run start
```
