import os
import queue
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from multiprocessing.pool import ThreadPool
from pathlib import Path

from config import Config, init_config
from exception import UnpackException
from log import only_logger, logger
from util7zip.util_7z import Util7z
from utils import abs_path, read_file, path_join, dict_format_str, write_file, title_format, time_diff, str_rep, \
    remove_file


class PackFileStatus(Enum):
    UNPACK_SUCCESS = '解压成功'
    UNPACK_FAIL = '解压失败'
    TEST_SUCCESS = '测试成功'
    TEST_FAIL = '测试失败'
    SKIP = '放弃解压'
    WAIT = '等待解压'


@dataclass
class PackFile(object):
    # 文件名称
    name: str = ''
    # 文件父路径
    path: str = ''
    # 文件状态
    status: PackFileStatus = PackFileStatus.WAIT
    # 密码
    password: str = ''
    # 解压路径
    output_path: str = ''

    def get_file_path(self) -> str:
        return str(Path(self.path, self.name))

    def __str__(self):
        return f'[{self.status.value}]' \
               f'文件名:[{self.name}]' \
               f'密码:[{self.password}]' \
               f'文件路径:[{self.path}]' \
               f'解压路径:[{self.output_path}]'


@dataclass
class Stat(object):
    # 过滤时间
    scan_start_time: datetime = datetime.now()
    scan_end_time: datetime = datetime.now()
    # 测试时间
    test_start_time: datetime = datetime.now()
    test_end_time: datetime = datetime.now()
    # 解压时间
    unpack_start_time: datetime = datetime.now()
    unpack_end_time: datetime = datetime.now()

    scan_file_sum: int = 0
    skip_file_sum: int = 0
    unpack_fail_file_sum: int = 0
    test_fail_file_sum: int = 0
    unpack_success_file_sum: int = 0
    test_success_file_sum: int = 0

    def __str__(self):
        return '\n'.join([
            f'筛选文件时长:{time_diff(self.scan_start_time, self.scan_end_time)}秒',
            f'测试文件时长:{time_diff(self.test_start_time, self.test_end_time)}秒',
            f'解压文件时长:{time_diff(self.unpack_start_time, self.unpack_end_time)}秒',
            str_rep('-'),
            f'总共发现文件:{self.scan_file_sum}个',
            str_rep('-'),
            f'放弃解压总数:{self.skip_file_sum}个',
            f'测试失败总数:{self.test_fail_file_sum}个',
            f'测试成功总数:{self.test_success_file_sum}个',
            f'解压失败总数:{self.unpack_fail_file_sum}个',
            f'解压成功总数:{self.unpack_success_file_sum}个',
        ])


class AutoUnpack(object):
    _banner_path: str = abs_path('./banner')
    _banner: str = ''
    _config_path: str = abs_path('./config.yaml')
    _config: Config
    _passwords_path: str = abs_path('./passwords.txt')
    _passwords: set = {''}
    _pack_files: [PackFile] = []
    _test_pack_file_queue = queue.Queue(maxsize=1)
    _unpack_report_path: str = abs_path('./report.txt')
    _unpack_report: str = ''
    _stat: Stat = Stat()

    @classmethod
    def _stat_sum(cls, stat: PackFileStatus):
        return len([item for item in cls._pack_files if item.status == stat])

    @classmethod
    def _show_banner(cls):
        cls._banner = read_file(cls._banner_path)
        [only_logger.info(line) for line in cls._banner.split('\n')]

    @classmethod
    def _load_config(cls):
        logger.info('开始加载配置')
        cls._config = init_config(cls._config_path)
        logger.info('加载配置完成')
        config_format: str = dict_format_str(cls._config.as_dict())
        [only_logger.info(line) for line in config_format.split('\n')]

    @classmethod
    def _load_passwords(cls):
        logger.info('开始加载密码表')
        password_line = read_file(cls._passwords_path).split('\n')
        cls._passwords = cls._passwords.union(password_line)
        logger.info('加载密码表完成')
        logger.info(f'[{",".join(cls._passwords)}]')

    @classmethod
    def _scan_pack(cls):
        logger.info('筛选文件开始')
        cls._stat.scan_start_time = datetime.now()
        for fa, dirs, fs in os.walk(cls._config.path.pack_path):
            for file_name in fs:
                # 匹配文件名称
                is_pack_filter = len(re.findall(cls._config.pack_filter.filter_re, file_name)) > 0

                is_match = False
                if cls._config.pack_filter.filter_include_model and is_pack_filter:
                    # 包含模式
                    is_match = True
                elif not cls._config.pack_filter.filter_include_model and not is_pack_filter:
                    # 排除模式
                    is_match = True
                pack_file = PackFile(name=file_name, path=fa,
                                     status=PackFileStatus.WAIT if is_match else PackFileStatus.SKIP)
                cls._pack_files.append(pack_file)

            if not cls._config.base.deep_pack_file:
                break
        logger.info('筛选文件完成')
        cls._stat.scan_end_time = datetime.now()
        cls._stat.scan_file_sum = len(cls._pack_files)
        cls._stat.skip_file_sum = cls._stat_sum(PackFileStatus.SKIP)
        [logger.info(f'{item}') for item in cls._pack_files]

    @classmethod
    def _test_pack(cls):
        pool = ThreadPool(cls._config.base.test_pack_thread_pool_max)
        logger.info('测试文件开始')
        cls._stat.test_start_time = datetime.now()

        def test_pack_file(pack_file_item: PackFile):
            # 调用 7zip 测试压缩包
            for password in cls._passwords:
                (status, test_info) = Util7z.test(pack_file_item.get_file_path(), password)
                if status == 0:
                    # 测试成功
                    pack_file_item.status = PackFileStatus.TEST_SUCCESS
                    # 顺便记录密码
                    pack_file_item.password = password
                    break
            else:
                # 测试失败
                pack_file_item.status = PackFileStatus.TEST_FAIL

            logger.info(f'{pack_file_item}')

        for pack_file in filter(lambda item: item.status == PackFileStatus.WAIT, cls._pack_files):
            # 获取全部 WAIT 状态的文件
            pool.apply_async(test_pack_file, kwds={'pack_file_item': pack_file})
        pool.close()
        pool.join()
        logger.info('测试文件完成')
        cls._stat.test_end_time = datetime.now()
        cls._stat.test_fail_file_sum = cls._stat_sum(PackFileStatus.TEST_FAIL)
        cls._stat.test_success_file_sum = cls._stat_sum(PackFileStatus.TEST_SUCCESS)

    @classmethod
    def _unpack(cls):
        pool = ThreadPool(cls._config.base.unpack_thread_pool_max)
        logger.info('解压文件开始')
        cls._stat.unpack_start_time = datetime.now()

        def unpack_file(pack_file_item: PackFile):
            unpack_path = cls._config.path.unpack_path

            if cls._config.base.parcel_unpack_file:
                unpack_path = path_join(unpack_path, pack_file_item.name)

            (status, unpack_info) = Util7z.unpack(file_path=pack_file_item.get_file_path(),
                                                  password=pack_file_item.password,
                                                  unpack_path=unpack_path,
                                                  over_write_model=cls._config.base.unpack_over_write_model,
                                                  keep_dir=cls._config.base.keep_dir)

            if status == 0:
                pack_file_item.status = PackFileStatus.UNPACK_SUCCESS
                pack_file_item.output_path = unpack_path
                if cls._config.base.unpack_success_del:
                    # 解压成功删除文件
                    remove_file(pack_file_item.get_file_path())
            else:
                pack_file_item.status = PackFileStatus.UNPACK_FAIL

            logger.info(f'{pack_file_item}')

        for pack_file in filter(lambda item: item.status == PackFileStatus.TEST_SUCCESS, cls._pack_files):
            # 获取全部 WAIT 状态的文件
            pool.apply_async(unpack_file, kwds={'pack_file_item': pack_file})

        pool.close()
        pool.join()
        logger.info('解压文件完成')
        cls._stat.unpack_end_time = datetime.now()
        cls._stat.unpack_fail_file_sum = cls._stat_sum(PackFileStatus.UNPACK_FAIL)
        cls._stat.unpack_success_file_sum = cls._stat_sum(PackFileStatus.UNPACK_SUCCESS)

    @classmethod
    def _create_unpack_report(cls):
        unpack_report_list = [
            cls._banner,
            title_format('配置信息', 100, '=', f'{cls._config}'),
            title_format('统计信息', 100, '=', f'{cls._stat}'),
            title_format('详细信息', 100, '=', *[str(item) for item in cls._pack_files]),
        ]

        cls._unpack_report = '\n'.join(unpack_report_list)
        write_file(cls._unpack_report_path, data=cls._unpack_report)
        logger.info(f'详细统计信息见:{cls._unpack_report_path}')

    @classmethod
    def _run_auto_unpack(cls):
        # 显示 banner
        cls._show_banner()
        # 加载配置
        cls._load_config()
        # 加载密码表
        cls._load_passwords()
        # 扫描 pack 文件
        cls._scan_pack()
        # 测试压缩包完整性和密码
        cls._test_pack()
        # 解压压缩包
        cls._unpack()
        # 生成解压报告
        cls._create_unpack_report()

    @classmethod
    def start_unpack(cls):
        try:
            cls._run_auto_unpack()
        except UnpackException as e:
            logger.error(f'程序出现错误! 原因:{e}')
            sys.exit(1)
        except Exception as e:
            logger.error(f'程序出现意外错误! 原因:{e}')
            sys.exit(2)


if __name__ == '__main__':
    AutoUnpack.start_unpack()
