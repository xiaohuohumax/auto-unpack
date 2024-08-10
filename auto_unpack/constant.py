from pathlib import Path

# 内置插件目录
BUILTIN_PLUGINS_DIR: Path = Path(__file__).parent/'plugins'
# 上下文默认key
CONTEXT_DEFAULT_KEY: str = "default"
# 初始化模板目录
INIT_TEMPLATE_DIR = Path(__file__).parent/'template'
