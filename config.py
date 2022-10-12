from dataclasses import dataclass, asdict, field

from dacite import from_dict
from ruamel import yaml

from exception import UnpackException
from utils import abs_path, title_format, exists_file, read_file


@dataclass
class ConfigBase:
    unpack_success_del: bool = False
    unpack_thread_pool_max: int = 10
    test_pack_thread_pool_max: int = 20
    unpack_over_write_model: str = 't'
    parcel_unpack_file: bool = True
    keep_dir: bool = True
    deep_pack_file: bool = True

    def __post_init__(self):
        unpack_over_write_model_allow = ['a', 's', 't', 'u']
        if self.unpack_over_write_model not in unpack_over_write_model_allow:
            raise UnpackException(f'提取文件覆写模式只能选择{unpack_over_write_model_allow}')

    def __str__(self):
        return '\n'.join([
            f'解压成功后是否删除压缩包:{self.unpack_success_del}',
            f'并发解压的数量上限:{self.unpack_thread_pool_max}',
            f'并发测试压缩包的数量上限:{self.test_pack_thread_pool_max}',
            f'提取文件覆写模式:{self.unpack_over_write_model}',
            f'是否将压缩包解压的文件放进新文件夹中:{self.parcel_unpack_file}',
            f'解压是否保持文件的层级关系:{self.keep_dir}',
            f'自动解压是否包含子文件夹:{self.deep_pack_file}',
        ])


@dataclass
class ConfigPath:
    passwords_path: str = './passwords.txt'
    pack_path: str = './pack'
    unpack_path: str = './unpack'

    def __post_init__(self):
        self.passwords_path = abs_path(self.passwords_path)
        self.pack_path = abs_path(self.pack_path)
        self.unpack_path = abs_path(self.unpack_path)

        if not exists_file(self.passwords_path):
            raise UnpackException(f'密码表路径不存在:{self.passwords_path}')
        if not exists_file(self.pack_path):
            raise UnpackException(f'待解压压缩包路径:{self.pack_path}')

    def __str__(self):
        return '\n'.join([
            f'密码表路径:{self.passwords_path}',
            f'待解压压缩包路径:{self.pack_path}',
            f'压缩包解压完成存放路径:{self.unpack_path}',
        ])


@dataclass
class ConfigPackFilter:
    filter_include_model: bool = True
    filter_re: str = '.*'

    def __str__(self):
        return '\n'.join([
            f'过滤模式:{self.filter_include_model}',
            f'压缩包过滤筛选正则:{self.filter_re}',
        ])


@dataclass
class Config:
    path: ConfigPath = field(default_factory=lambda: ConfigPath())
    base: ConfigBase = field(default_factory=lambda: ConfigBase())
    pack_filter: ConfigPackFilter = field(default_factory=lambda: ConfigPackFilter())

    def as_dict(self):
        return asdict(self)

    def __str__(self):
        return '\n'.join([
            title_format('[基础配置]', 100, '-', f'{self.base}'),
            title_format('[路径配置]', 100, '-', f'{self.path}'),
            title_format('[压缩包文件过滤配置]', 100, '-', f'{self.pack_filter}'),
        ])


def init_config(config_path: str) -> Config:
    config_yaml_data = read_file(config_path)
    return from_dict(data_class=Config, data=yaml.safe_load(config_yaml_data))


if __name__ == '__main__':
    print(init_config('./config.yaml').__str__())
