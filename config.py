import logging
from dataclasses import dataclass, field
from typing import List

from dacite import from_dict
from ruamel import yaml

import utils
from core import PackFileStatusEnum, KeysValuesEnum, UnpackException


@dataclass
class ConfigPackPath:
    passwords: str = './passwords.txt'
    pack: str = './pack'
    unpack: str = './unpack'
    report: str = './report.txt'

    def __post_init__(self):
        self.passwords = utils.abs_path(self.passwords)
        self.pack = utils.abs_path(self.pack)
        self.unpack = utils.abs_path(self.unpack)
        self.report = utils.abs_path(self.report)

        if not utils.is_exists_file(self.passwords):
            raise UnpackException(f'路径配置-密码表不存在:{self.passwords}')
        if not utils.is_exists_file(self.pack):
            raise UnpackException(f'路径配置-压缩包存放路径不存在:{self.pack}')

    def __str__(self):
        return '\n'.join([
            f'密码表路径:{self.passwords}',
            f'压缩包存放路径:{self.pack}',
            f'压缩包解压存放路径:{self.unpack}',
            f'解压报告存放路径:{self.report}',
        ])


class LogLevelEnum(KeysValuesEnum):
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    CRITICAL = logging.CRITICAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING


@dataclass
class ConfigPackGlobal:
    log_level: str = LogLevelEnum.INFO.name
    log_level_obj: LogLevelEnum = field(init=False)

    def __post_init__(self):
        self.log_level = self.log_level.lower()
        self.log_level_obj = LogLevelEnum.init_by_key(self.log_level)

        if self.log_level_obj is None:
            raise UnpackException(f'全局配置-日志等级异常:{self.log_level}')

    def __str__(self):
        return '\n'.join([
            f'日志等级:{self.log_level}',
        ])


@dataclass
class ConfigPackScan:
    is_deep_scan: bool = True

    def __str__(self):
        return '\n'.join([
            f'是否扫描子文件夹:{utils.bool_map(self.is_deep_scan)}',
        ])


class PackRenameEnum(KeysValuesEnum):
    REPLACE = 'replace'
    GROUP = 'group'


@dataclass(init=False)
class PackRenameRuleChain:
    module: PackRenameEnum = None

    # REPLACE
    replace_old: str = ''
    replace_new: str = ''

    # GROUP
    group_pattern: str = ''
    group_repl: str = ''

    def __init__(self, rule: str):
        try:
            rule_command_list = rule.split(':')
            self.module = PackRenameEnum.init_by_key(rule_command_list[0])

            if self.module is None:
                raise

            if self.module == PackRenameEnum.REPLACE:
                # 替换模式
                self.replace_old = rule_command_list[1]
                self.replace_new = rule_command_list[2]
            elif self.module == PackRenameEnum.GROUP:
                # 捕获组模式
                self.group_pattern = rule_command_list[1]
                self.group_repl = rule_command_list[2]

        except Exception as _:
            raise UnpackException(f'压缩包改名配置-规则链格式异常:{rule}')


@dataclass
class ConfigPackRename:
    is_open: bool = False
    rule_chain: List[str] = field(default_factory=list)
    rule_chain_obj: List[PackRenameRuleChain] = field(init=False)

    def __post_init__(self):
        self.rule_chain_obj = [PackRenameRuleChain(rule) for rule in self.rule_chain]

    def __str__(self):
        return '\n'.join([
            f'是否执行改名操作:{utils.bool_map(self.is_open)}',
            f'规则链:{self.rule_chain}',
        ])


class PackFilterEnum(KeysValuesEnum):
    INCLUDE = 'include'
    EXCLUDE = 'exclude'


@dataclass(init=False)
class PackFilterRuleChain:
    module: PackFilterEnum = None

    # INCLUDE
    include_re: str = ''

    # EXCLUDE
    exclude_re: str = ''

    def __init__(self, rule: str):
        try:
            rule_command_list = rule.split(':')
            self.module = PackFilterEnum.init_by_key(rule_command_list[0])

            if self.module is None:
                raise

            if self.module == PackFilterEnum.INCLUDE:
                # 包含模式
                self.include_re = rule_command_list[1]
            elif self.module == PackFilterEnum.EXCLUDE:
                # 排除模式
                self.exclude_re = rule_command_list[1]

        except Exception as _:
            raise UnpackException(f'压缩包过滤配置-规则链格式异常:{rule}')


@dataclass
class ConfigPackFilter:
    is_open: bool = False
    rule_chain: List[str] = field(default_factory=list)
    rule_chain_obj: List[PackFilterRuleChain] = field(init=False)

    def __post_init__(self):
        self.rule_chain_obj = [PackFilterRuleChain(rule) for rule in self.rule_chain]

    def __str__(self):
        return '\n'.join([
            f'是否执行过滤操作:{utils.bool_map(self.is_open)}',
            f'规则链:{self.rule_chain}',
        ])


@dataclass
class ConfigPackAnalysis:
    is_open: bool = True
    thread_pool_max: int = 20

    def __post_init__(self):
        if self.thread_pool_max < 1:
            raise UnpackException(f'压缩包识别配置-并发识别数量上限异常:{self.thread_pool_max}')

    def __str__(self):
        return '\n'.join([
            f'是否执行识别操作:{utils.bool_map(self.is_open)}',
            f'并发识别数量上限:{self.thread_pool_max}',
        ])


@dataclass
class ConfigPackTest:
    is_open: bool = True
    thread_pool_max: int = 10

    def __post_init__(self):
        if self.thread_pool_max < 1:
            raise UnpackException(f'压缩包测试配置-并发测试数量上限异常:{self.thread_pool_max}')

    def __str__(self):
        return '\n'.join([
            f'是否执行测试操作:{utils.bool_map(self.is_open)}',
            f'并发测试数量上限:{self.thread_pool_max}',
        ])


class PackOverwriteModelEnum(KeysValuesEnum):
    A = 'a'
    S = 's'
    T = 't'
    U = 'u'


class PackParcelUnpackFileEnum(KeysValuesEnum):
    ALWAYS = 'always'
    AUTO = 'auto'
    NEVER = 'never'


@dataclass
class ConfigPackUnpack:
    is_open: bool = True
    parcel_unpack_file: str = PackParcelUnpackFileEnum.ALWAYS.name
    parcel_unpack_file_obj: PackParcelUnpackFileEnum = field(init=False)
    is_keep_dir: bool = True
    overwrite_model: str = PackOverwriteModelEnum.U.name
    overwrite_model_obj: PackOverwriteModelEnum = field(init=False)
    is_success_del: bool = False
    thread_pool_max: int = 5

    def __post_init__(self):
        self.overwrite_model = self.overwrite_model.lower()
        self.overwrite_model_obj = PackOverwriteModelEnum.init_by_key(self.overwrite_model)
        self.parcel_unpack_file_obj = PackParcelUnpackFileEnum.init_by_key(self.parcel_unpack_file)

        if self.overwrite_model_obj is None:
            raise UnpackException(f'压缩包解压配置-提取文件覆写模式异常:{self.overwrite_model}')

        if self.parcel_unpack_file_obj is None:
            raise UnpackException(f'压缩包解压配置-解压文件创建包裹文件夹异常:{self.parcel_unpack_file}')

        if self.thread_pool_max < 1:
            raise UnpackException(f'压缩包解压配置-并发测试数量上限异常:{self.thread_pool_max}')

    def __str__(self):
        return '\n'.join([
            f'是否执行解压操作:{utils.bool_map(self.is_open)}',
            f'解压文件创建包裹文件夹:{self.parcel_unpack_file}',
            f'是否保持压缩包解压文件的层级关系:{utils.bool_map(self.is_keep_dir)}',
            f'解压文件覆写模式:{self.overwrite_model}',
            f'是否删除解压成功的压缩包:{utils.bool_map(self.is_success_del)}',
            f'并发解压数量上限:{self.thread_pool_max}',
        ])


@dataclass
class ConfigPackClear:
    is_open: bool = False
    is_del_pack_empty_folder: bool = False
    is_del_unpack_empty_folder: bool = False
    is_format_passwords: bool = False

    def __str__(self):
        return '\n'.join([
            f'是否执行清理操作:{utils.bool_map(self.is_open)}',
            f'是否删除压缩包存放文件夹中的空文件夹:{utils.bool_map(self.is_del_pack_empty_folder)}',
            f'是否删除压缩包解压存放文件夹中的空文件夹:{utils.bool_map(self.is_del_unpack_empty_folder)}',
            f'是否整理密码表:{utils.bool_map(self.is_format_passwords)}',
        ])


@dataclass
class ConfigPackReport:
    is_show_config: bool = True
    is_show_status: bool = True
    is_show_pack_info: bool = True
    show_pack_status: List[str] = field(default_factory=lambda: ['all'])

    def __post_init__(self):
        self.show_pack_status = [item.lower() for item in self.show_pack_status]

        if 'all' in self.show_pack_status:
            self.show_pack_status = [item.lower() for item in PackFileStatusEnum.keys()]
        else:
            for status in self.show_pack_status:
                if status not in PackFileStatusEnum.keys():
                    raise UnpackException(f'解压报告配置-显示压缩包解压状态类型异常:{status.lower()}')

    def __str__(self):
        return '\n'.join([
            f'是否显示配置信息:{utils.bool_map(self.is_show_config)}',
            f'是否显示统计信息:{utils.bool_map(self.is_show_status)}',
            f'是否显示压缩包解压信息:{utils.bool_map(self.is_show_pack_info)}',
            f'显示压缩包解压状态类型:{self.show_pack_status}',
        ])


@dataclass
class Config:
    pack_path: ConfigPackPath = field(default_factory=lambda: ConfigPackPath())
    pack_global: ConfigPackGlobal = field(default_factory=lambda: ConfigPackGlobal())
    pack_scan: ConfigPackScan = field(default_factory=lambda: ConfigPackScan())
    pack_rename: ConfigPackRename = field(default_factory=lambda: ConfigPackRename())
    pack_filter: ConfigPackFilter = field(default_factory=lambda: ConfigPackFilter())
    pack_analysis: ConfigPackAnalysis = field(default_factory=lambda: ConfigPackAnalysis())
    pack_test: ConfigPackTest = field(default_factory=lambda: ConfigPackTest())
    pack_unpack: ConfigPackUnpack = field(default_factory=lambda: ConfigPackUnpack())
    pack_clear: ConfigPackClear = field(default_factory=lambda: ConfigPackClear())
    pack_report: ConfigPackReport = field(default_factory=lambda: ConfigPackReport())

    def __str__(self):
        return '\n'.join([
            utils.title_format('[路径配置]', 100, '-', f'{self.pack_path}'),
            utils.title_format('[全局配置]', 100, '-', f'{self.pack_global}'),
            utils.title_format('[压缩包扫描配置]', 100, '-', f'{self.pack_scan}'),
            utils.title_format('[压缩包改名配置]', 100, '-', f'{self.pack_rename}'),
            utils.title_format('[压缩包过滤配置]', 100, '-', f'{self.pack_filter}'),
            utils.title_format('[压缩包识别配置]', 100, '-', f'{self.pack_analysis}'),
            utils.title_format('[压缩包测试配置]', 100, '-', f'{self.pack_test}'),
            utils.title_format('[压缩包解压配置]', 100, '-', f'{self.pack_unpack}'),
            utils.title_format('[压缩包清理配置]', 100, '-', f'{self.pack_clear}'),
            utils.title_format('[解压报告配置]', 100, '-', f'{self.pack_report}'),
            utils.str_rep('-', 100),
        ])


def init_config(config_path: str) -> Config:
    # 初始化配置
    if config_path is None:
        # 采用默认配置
        return Config()
    config_yaml_data = utils.read_file(config_path)
    # 替换默认配置
    return from_dict(data_class=Config, data=yaml.safe_load(config_yaml_data))


if __name__ == '__main__':
    print(init_config('./config.yaml'))
