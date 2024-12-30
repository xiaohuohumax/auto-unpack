import argparse
import json
import os
import shutil
import sys
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import inquirer
from inquirer.errors import ValidationError
from pydantic import BaseModel, Field

from . import __owner__, __repo__, __version__, constant, schema
from .args import CustomHelpFormatter
from .plugin import PluginManager
from .util import download, file

release_json_name = "release.json"
cli_parent_dir = Path(__file__).parent


class TemplateAsset(BaseModel):
    """
    模板资产
    """

    name: str = Field(description="模板名称")
    description: str = Field(description="模板描述")
    asset_name: str = Field(description="模板资产名称")


class ReleaseAsset(BaseModel):
    """
    发布资产
    """

    version: str = Field(
        # 资产版本号，版本号不同则表示不兼容
        default="1",
        description="版本号",
    )
    release_version: str = Field(default="v" + __version__, description="发布版本号")
    templates: List[TemplateAsset] = Field(default=[], description="模板资产列表")


class ArgsSubCommand(Enum):
    """
    子命令枚举
    """

    # 初始化项目
    INIT = "init"
    # 生成 schema
    SCHEMA = "schema"


class Args(BaseModel):
    """
    命令行参数
    """

    # 是否显示版本号
    version: bool = False
    # 子命令
    sub_command: Optional[ArgsSubCommand] = None

    # INIT 参数
    dir: str = ""
    template: str = ""
    latest: bool = False

    # SCHEMA 参数
    # 是否忽略内置插件
    ignore_builtin_plugins: bool = False
    # 自定义插件目录/文件
    plugin_paths: List[str] = []
    # schema 输出文件路径
    schema_output: str = ""


class SubParser:
    command: ArgsSubCommand
    help: str
    subparser: argparse.ArgumentParser

    def __init__(self, subparser: argparse._SubParsersAction):
        self.subparser = subparser.add_parser(
            self.command.value, help=self.help, formatter_class=CustomHelpFormatter
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
    help = "初始化项目"
    # 文件名映射
    file_name_map: Dict[str, str] = {
        "_gitignore": ".gitignore",
    }
    # 缓存目录
    cache_dir = constant.PKG_CACHE_DIR / "cli"

    def __init__(self, subparser: argparse._SubParsersAction):
        super(InitSubParser, self).__init__(subparser)
        self.subparser.set_defaults(sub_command=ArgsSubCommand.INIT)

        self.subparser.add_argument(
            "dir", type=str, nargs="?", help="初始化项目目录", default=""
        )
        self.subparser.add_argument(
            "-l",
            "--latest",
            action="store_true",
            help="是否使用最新模板",
            default=False,
        )

    def _dir_validation(self, _, current) -> True:
        """
        验证初始化目录是否合法

        :param _: _description_
        :param current: 目录
        :raises ValidationError: 验证失败
        :return: True
        """
        p = Path(os.getcwd()) / current
        if p.exists():
            if p.is_file():
                raise ValidationError("", reason="存在同名文件，请重新输入")
            elif list(p.iterdir()):
                raise ValidationError("", reason="目录不为空，请重新输入")
        return True

    def _get_release_asset_url(self, version: str, asset_name: str) -> str:
        """
        获取 release 资产下载地址

        :param version: 版本号
        :param asset_name: 资产名称
        :return: 下载地址
        """
        if version == "latest":
            return f"https://github.com/{__owner__}/{__repo__}/releases/latest/download/{asset_name}"
        return f"https://github.com/{__owner__}/{__repo__}/releases/download/{version}/{asset_name}"

    def _get_release_asset(self, args: Args) -> Tuple[str, List[TemplateAsset]]:
        """
        获取 release 资产

        :return: 版本号，模板资产列表
        """
        local_release = ReleaseAsset.model_validate_json(
            file.read_file(cli_parent_dir / release_json_name)
        )

        release_version = local_release.release_version
        templates = local_release.templates

        if args.latest:
            latest_release: Optional[ReleaseAsset] = None
            latest_release_url = self._get_release_asset_url(
                "latest", release_json_name
            )

            latest_release_file = self.cache_dir / release_json_name
            try:
                print("Downloading latest release config...")
                download.download_url(latest_release_url, latest_release_file)

                latest_release = ReleaseAsset.model_validate_json(
                    file.read_file(latest_release_file)
                )
            except:
                print(
                    "Failed to download latest release config, use local release config..."
                )

            if (
                latest_release is not None
                and local_release.version == latest_release.version
            ):
                release_version = latest_release.release_version
                templates = latest_release.templates

            print(f"Release version: {release_version}")

        return release_version, templates

    def execute(self, args: Args):
        """
        执行初始化

        :param args: 命令行参数
        """
        release_version, template_assets = self._get_release_asset(args)
        # 下载模板资产映射
        questions = [
            inquirer.Text(
                name="dir",
                message="请输入初始化项目目录",
                validate=self._dir_validation,
            ),
            inquirer.List(
                name="template",
                message="请选择模板",
                choices=[t.description for t in template_assets],
            ),
        ]
        answers = inquirer.prompt(questions, answers=vars(args))
        if answers is None:
            return

        answers = Args(**answers)

        # 获取资源名称
        asset_name = next(
            (
                t.asset_name
                for t in template_assets
                if t.description == answers.template
            ),
            None,
        )

        template_asset_file = self.cache_dir / release_version / asset_name
        if not template_asset_file.exists():
            try:
                # 本地缓存不存在，下载模板
                template_asset_url = self._get_release_asset_url(
                    release_version, asset_name
                )
                print(f"Downloading {template_asset_url} to {template_asset_file}")
                download.download_url(template_asset_url, template_asset_file)
            except Exception as e:
                print(f"Download template {asset_name} failed: {e}")
                sys.exit(1)

        shutil.unpack_archive(template_asset_file, extract_dir=answers.dir)

        # 通过文件名映射重命名文件
        for file_name, new_file_name in InitSubParser.file_name_map.items():
            file_path = Path(answers.dir) / file_name
            if file_path.exists():
                new_file_path = Path(answers.dir) / new_file_name
                file_path.rename(new_file_path)

        print("Initialized finished!\n")
        print(f"  cd {answers.dir}\n  rye sync")


class SchemaSubParser(SubParser):
    command: ArgsSubCommand = ArgsSubCommand.SCHEMA
    help = "生成JSON Schema"

    def __init__(self, subparser: argparse._SubParsersAction):
        super(SchemaSubParser, self).__init__(subparser)

        self.subparser.set_defaults(sub_command=ArgsSubCommand.SCHEMA)

        self.subparser.add_argument(
            "-i",
            "--ignore-builtin-plugins",
            action="store_true",
            help="是否忽略内置插件",
            default=False,
        )

        self.subparser.add_argument(
            "plugin_paths", type=str, nargs="*", help="自定义插件目录/文件"
        )

        self.subparser.add_argument(
            "-o",
            "--schema-output",
            type=str,
            help="schema 输出文件路径",
            default="schema/auto-unpack-flow-schema.json",
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

        flow_schema_dict = schema.generate_flow_schema(plugin_manager=plugin_manager)

        schema_output = Path(args.schema_output)
        flow_schema = json.dumps(flow_schema_dict, ensure_ascii=False, indent=4)
        file.write_file(schema_output, flow_schema)

        print("Schema generated finished!")
        print(f"Schema output: {schema_output}")


def main():
    """
    脚手架工具入口
    """
    parser = argparse.ArgumentParser(
        description="auto-unpack 脚手架工具，用于快速创建项目",
        formatter_class=CustomHelpFormatter,
    )
    parser.add_argument("-v", "--version", action="store_true", help="显示版本号")

    subparser = parser.add_subparsers(help="子命令", dest="sub_command")

    sub_parsers: List[SubParser] = [
        InitSubParser(subparser),
        SchemaSubParser(subparser),
    ]

    args = Args.model_validate(vars(parser.parse_args()))

    if args.version:
        print(__version__)
    elif args.sub_command is None:
        parser.print_help()
    else:
        for p in sub_parsers:
            if p.command is not None and p.command == args.sub_command:
                p.execute(args)
                break


if __name__ == "__main__":
    main()
