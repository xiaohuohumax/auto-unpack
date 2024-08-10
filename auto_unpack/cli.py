import argparse
import os
import shutil
from enum import Enum
from pathlib import Path
from typing import Dict, Optional

import inquirer
from inquirer.errors import ValidationError
from pydantic import BaseModel

from . import __version__ as version
from . import constant

# 定义模板目录
TEMPLATES: Dict[str, Path] = {
    "简单项目模板": constant.INIT_TEMPLATE_DIR/'simple-project',
    "自定义插件模板": constant.INIT_TEMPLATE_DIR/'custom-plugin',
    "后台服务模板": constant.INIT_TEMPLATE_DIR/'backend-service'
}

# 文件名映射
FILE_NAME_MAP: Dict[str, str] = {
    '_gitignore': '.gitignore',
}


class ArgsSubCommand(Enum):
    """
    子命令枚举
    """
    INIT = 'init'


class Args(BaseModel):
    """
    命令行参数
    """
    # 是否显示版本号
    version: bool = False
    # 子命令
    sub_command: Optional[ArgsSubCommand] = None

    # INIT 参数
    init_dir: str = ''
    init_template: str = ''


def init(args: Args):
    """
    处理子命令 init: 初始化项目

    :param args: 命令行参数
    """

    def init_dir_validation(_, current) -> True:
        """
        验证初始化目录是否合法

        :param _: _description_
        :param current: 目录
        :raises ValidationError: 验证失败
        :return: True
        """
        p = Path(os.getcwd())/current
        if p.exists():
            if p.is_file():
                raise ValidationError("", reason="存在同名文件，请重新输入")
            elif list(p.iterdir()):
                raise ValidationError("", reason="目录不为空，请重新输入")
        return True

    questions = [
        inquirer.Text(
            name='init_dir', message='请输入初始化项目目录', validate=init_dir_validation),
        inquirer.List(
            name='init_template', message='请选择模板', choices=list(TEMPLATES.keys()))
    ]
    answers = inquirer.prompt(questions, answers=vars(args))
    if answers is None:
        return

    answers = Args(**answers)

    # 复制模板目录到初始化目录
    template_dir = TEMPLATES[answers.init_template]
    shutil.copytree(template_dir, answers.init_dir, dirs_exist_ok=True)

    # 通过文件名映射重命名文件
    for file_name, new_file_name in FILE_NAME_MAP.items():
        file_path = Path(answers.init_dir)/file_name
        if file_path.exists():
            new_file_path = Path(answers.init_dir)/new_file_name
            file_path.rename(new_file_path)

    print('Initialized finished!\n')
    print(f"  cd {answers.init_dir}\n  rye sync")


class CustomHelpFormatter(argparse.HelpFormatter):
    """
    自定义帮助信息格式
    """

    def _format_action_invocation(self, action):
        """
        格式化命令行参数

        :param action: 命令行参数
        :return: 格式化后的命令行参数
        """
        if action.option_strings and action.help:
            if '-h' in action.option_strings or '--help' in action.option_strings:
                action.help = '显示此帮助信息并退出'
        return super(CustomHelpFormatter, self)._format_action_invocation(action)


def main():
    """
    脚手架工具入口
    """
    parser = argparse.ArgumentParser(
        description="auto-unpack 脚手架工具，用于快速创建项目",
        formatter_class=CustomHelpFormatter
    )
    parser.add_argument('-v', '--version', action='store_true', help='显示版本号')

    subparser = parser.add_subparsers(help='子命令', dest='sub_command')

    init_parser = subparser.add_parser(
        ArgsSubCommand.INIT.value,
        help='初始化项目',
        formatter_class=CustomHelpFormatter
    )
    init_parser.set_defaults(sub_command=ArgsSubCommand.INIT)

    init_parser.add_argument('init_dir', type=str,
                             nargs='?', help='初始化项目目录', default='')

    args = Args.model_validate(vars(parser.parse_args()))

    if args.version:
        print(version)
    elif args.sub_command is None:
        parser.print_help()
    elif args.sub_command == ArgsSubCommand.INIT:
        init(args)


if __name__ == '__main__':
    main()
