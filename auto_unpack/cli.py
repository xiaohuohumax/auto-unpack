import argparse
import json
import os
import shutil
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

import inquirer
from inquirer.errors import ValidationError
from pydantic import BaseModel

from . import __version__ as version
from . import constant, schema
from .args import CustomHelpFormatter
from .plugin import PluginManager
from .util import file


class ArgsSubCommand(Enum):
    """
    子命令枚举
    """
    # 初始化项目
    INIT = 'init'
    # 生成 schema
    SCHEMA = 'schema'


class Args(BaseModel):
    """
    命令行参数
    """
    # 是否显示版本号
    version: bool = False
    # 子命令
    sub_command: Optional[ArgsSubCommand] = None

    # INIT 参数
    dir: str = ''
    template: str = ''

    # SCHEMA 参数
    # 是否忽略内置插件
    ignore_builtin_plugins: bool = False
    # 自定义插件目录/文件
    plugin_paths: List[str] = []
    # schema 输出文件路径
    schema_output: str = ''


class SubParser:

    command: ArgsSubCommand
    help: str
    subparser: argparse.ArgumentParser

    def __init__(self, subparser: argparse._SubParsersAction):
        self.subparser = subparser.add_parser(
            self.command.value,
            help=self.help,
            formatter_class=CustomHelpFormatter
        )
        pass

    def execute(self, args: Args):
        """
        执行子命令

        :param args: 命令行参数
        """
        pass


class InitSubParser(SubParser):

    command: ArgsSubCommand = ArgsSubCommand.INIT
    help = '初始化项目'

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

    def __init__(self, subparser: argparse._SubParsersAction):
        super(InitSubParser, self).__init__(subparser)
        self.subparser.set_defaults(sub_command=ArgsSubCommand.INIT)

        self.subparser.add_argument(
            'dir', type=str, nargs='?',
            help='初始化项目目录', default=''
        )

    def _dir_validation(self, _, current) -> True:
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

    def execute(self, args: Args):
        """
        执行初始化

        :param args: 命令行参数
        """
        questions = [
            inquirer.Text(
                name='dir', message='请输入初始化项目目录', validate=self._dir_validation),
            inquirer.List(
                name='template', message='请选择模板', choices=list(InitSubParser.TEMPLATES.keys()))
        ]
        answers = inquirer.prompt(questions, answers=vars(args))
        if answers is None:
            return

        answers = Args(**answers)

        # 复制模板目录到初始化目录
        template_dir = InitSubParser.TEMPLATES[answers.template]
        shutil.copytree(template_dir, answers.dir, dirs_exist_ok=True)

        # 通过文件名映射重命名文件
        for file_name, new_file_name in InitSubParser.FILE_NAME_MAP.items():
            file_path = Path(answers.dir)/file_name
            if file_path.exists():
                new_file_path = Path(answers.dir)/new_file_name
                file_path.rename(new_file_path)

        print('Initialized finished!\n')
        print(f"  cd {answers.dir}\n  rye sync")


class SchemaSubParser(SubParser):

    command: ArgsSubCommand = ArgsSubCommand.SCHEMA
    help = '生成JSON Schema'

    def __init__(self, subparser: argparse._SubParsersAction):
        super(SchemaSubParser, self).__init__(subparser)

        self.subparser.set_defaults(sub_command=ArgsSubCommand.SCHEMA)

        self.subparser.add_argument(
            "-i", '--ignore-builtin-plugins',
            action='store_true',
            help='是否忽略内置插件', default=False
        )

        self.subparser.add_argument(
            'plugin_paths', type=str, nargs='*',
            help='自定义插件目录/文件'
        )

        self.subparser.add_argument(
            "-o", '--schema-output', type=str,
            help='schema 输出文件路径',
            default='schema/auto-unpack-flow-schema.json'
        )

    def execute(self, args: Args):
        """
        执行 schema 生成

        :param args: 命令行参数
        """
        plugin_manager = PluginManager()

        if not args.ignore_builtin_plugins:
            plugin_manager.load_plugin(constant.BUILTIN_PLUGINS_DIR)

        for plugin_path in args.plugin_paths:
            plugin_manager.load_plugin(Path(plugin_path))

        flow_schema_dict = schema.generate_flow_schema(
            plugin_manager=plugin_manager
        )

        schema_output = Path(args.schema_output)
        flow_schema = json.dumps(
            flow_schema_dict, ensure_ascii=False, indent=4
        )
        file.write_file(schema_output, flow_schema)

        print('Schema generated finished!')
        print(f"Schema output: {schema_output}")


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

    sub_parsers: List[SubParser] = [
        InitSubParser(subparser),
        SchemaSubParser(subparser)
    ]

    args = Args.model_validate(vars(parser.parse_args()))

    if args.version:
        print(version)
    elif args.sub_command is None:
        parser.print_help()
    else:
        for p in sub_parsers:
            if p.command is not None and p.command == args.sub_command:
                p.execute(args)
                break


if __name__ == '__main__':
    main()
