import argparse
from pathlib import Path
from typing import Optional

from pydantic import BaseModel


class Args(BaseModel):
    """
    命令行参数
    """

    # 模式
    mode: Optional[str] = None

    # 配置文件存放目录
    config_dir: Optional[Path] = None


class CustomHelpFormatter(argparse.HelpFormatter):
    """
    自定义帮助信息格式
    """

    def __init__(self, *args, **kwargs):
        super(CustomHelpFormatter, self).__init__(*args, **kwargs)
        self._max_help_position = 60

    def _format_action_invocation(self, action):
        """
        格式化命令行参数

        :param action: 命令行参数
        :return: 格式化后的命令行参数
        """
        if action.option_strings and action.help:
            if "-h" in action.option_strings or "--help" in action.option_strings:
                action.help = "显示此帮助信息并退出"
        return super(CustomHelpFormatter, self)._format_action_invocation(action)


def load_args() -> Args:
    """
    加载命令行参数

    :return: 命令行参数
    """
    parser = argparse.ArgumentParser(
        description="", formatter_class=CustomHelpFormatter
    )
    parser.add_argument(
        "-m", "--mode", dest="mode", type=str, default=None, help="运行模式"
    )
    parser.add_argument(
        "-c",
        "--config-dir",
        dest="config_dir",
        type=str,
        default=None,
        help="配置文件存放目录",
    )

    return Args.model_validate(vars(parser.parse_args()))
