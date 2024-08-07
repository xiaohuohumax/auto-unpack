# 配置校验

给配置文件添加校验功能，可以有效避免配置错误导致程序运行异常。

## JSON Schema 文件

| Schema 文件名                | 作用                                        |
| ---------------------------- | ------------------------------------------- |
| auto-unpack-schema.json      | 项目配置校验（application.yaml）            |
| auto-unpack-flow-schema.json | 验证流程配置校验（application.[mode].yaml） |

### CDN 地址

```txt
<!-- 最新 -->
https://cdn.jsdelivr.net/gh/xiaohuohumax/auto-unpack@main/schema/auto-unpack-schema.json
<!-- 特定版本 -->
https://cdn.jsdelivr.net/gh/xiaohuohumax/auto-unpack@main/schema/[version]/auto-unpack-schema.json

<!-- 最新 -->
https://cdn.jsdelivr.net/gh/xiaohuohumax/auto-unpack@main/schema/auto-unpack-flow-schema.json
<!-- 特定版本 -->
https://cdn.jsdelivr.net/gh/xiaohuohumax/auto-unpack@main/schema/[version]/auto-unpack-flow-schema.json
```

### Github 地址

```txt
<!-- 最新 -->
https://github.com/xiaohuohumax/auto-unpack/tree/main/schema/auto-unpack-schema.json
<!-- 特定版本 -->
https://github.com/xiaohuohumax/auto-unpack/tree/main/schema/[version]/auto-unpack-schema.json

<!-- 最新 -->
https://github.com/xiaohuohumax/auto-unpack/tree/main/schema/auto-unpack-flow-schema.json
<!-- 特定版本 -->
https://github.com/xiaohuohumax/auto-unpack/tree/main/schema/[version]/auto-unpack-flow-schema.json
```

## VSCode 中使用

1. 安装插件 `redhat.vscode-yaml`
2. 添加校验映射配置 `.vscode/settings.json`
```json
{
     "yaml.schemas": {
        // cdn
        // "https://cdn.jsdelivr.net/gh/xiaohuohumax/auto-unpack@main/schema/auto-unpack-schema.json": "config/application.yaml",
        // "https://cdn.jsdelivr.net/gh/xiaohuohumax/auto-unpack@main/schema/auto-unpack-flow-schema.json": "config/application.*.yaml",
        // local
        "schema/auto-unpack-schema.json": "config/application.yaml",
        "schema/auto-unpack-flow-schema.json": "config/application.*.yaml",
     },
}
```
