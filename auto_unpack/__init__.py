from .app import App
from .config import config
from .util.file import read_file
from .util.logging import config_logging

config_logging(config.logging.config_path, config.logging.level)


def print_banner():
    """
    打印 banner
    """
    if not config.banner.enabled:
        return

    if not config.banner.file_path.exists():
        return

    print(read_file(config.banner.file_path))
    print(config.banner.welcome + '\n')


print_banner()

__all__ = ["App"]
