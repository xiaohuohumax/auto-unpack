import os
import re
import sys
from functools import wraps
from itertools import groupby
from multiprocessing.pool import ThreadPool
from typing import List

import utils
from config import Config, init_config, PackRenameEnum, PackFilterEnum, PackParcelUnpackFileEnum
from core import PackFile, UnpackStat, PackFileStatusEnum, UnpackException, TimeDuration
from log import logger
from util7zip import Util7zResCodeEnum, Util7z


def error_history(tip_msg: str, error_status: PackFileStatusEnum):
    """
    压缩包处理过程异常捕获记录,且修改压缩包处理状态
    :param tip_msg: 异常时提示信息
    :param error_status: 异常时设置状态
    """

    def error_history_body(func):
        @wraps(func)
        def wrapper(cls, pack_file_item: PackFile):
            try:
                return func(cls, pack_file_item)
            except Exception as e:
                try:
                    error_info = f'{tip_msg}:{e}'
                    # 设置状态
                    pack_file_item.status = error_status
                    # 添加异常信息
                    pack_file_item.error_history.append(e)
                    logger.error(error_info)
                except Exception as error:
                    logger.error(f'捕获异常处理异常:{error}')

        return wrapper

    return error_history_body


def duration_time(time_duration: TimeDuration):
    """
    计算执行花费时长
    :param time_duration: 计时对象
    """

    def duration_time_body(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 开始计时
            time_duration.start()
            res = func(*args, **kwargs)
            # 结束计时
            time_duration.end()
            return res

        return wrapper

    return duration_time_body


def encircle_intercept(is_open_func: lambda cls: cls = lambda _: True, un_open_tip: str = '', start_tip: str = '',
                       end_tip: str = ''):
    """
    环绕拦截方法 输出信息 默认允许执行被装饰函数
    :param is_open_func: 是否执行被修饰函数 返回True/False 函数参数为 cls
    :param un_open_tip: 不执行时提示信息
    :param start_tip: 执行时 被装饰函数前输出信息
    :param end_tip: 执行时 被装饰函数后输出信息
    """

    def duration_time_body(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if is_open_func(args[0]):
                logger.info(start_tip)
                res = func(*args, **kwargs)
                logger.info(end_tip)
                return res
            else:
                logger.info(un_open_tip)

        return wrapper

    return duration_time_body


class AutoUnpack(object):
    """
    自动解压主入口类
    """

    _banner_path: str = utils.abs_path('./banner')
    _banner: str = ''
    _config_path: str = utils.abs_path('./config.yaml')
    _config: Config
    _passwords: set = set()
    _pack_files: List[PackFile] = []

    @classmethod
    def _each_file_by_status_callback(cls, status: List[PackFileStatusEnum], callback: lambda x: None):
        # 遍历当期为此状态的 压缩包文件列表
        [callback(pack_file) for pack_file in filter(lambda item: item.status in status, cls._pack_files)]

    @classmethod
    def _count_status_history(cls, status: List[PackFileStatusEnum]) -> int:
        # 统计某些状态的压缩包文件数量
        return len([pack_file_item for pack_file_item in cls._pack_files if pack_file_item.is_has_status(status)])

    @classmethod
    def _count_error_history(cls) -> int:
        # 统计存在异常的的压缩包文件数量
        return len([pack_file_item for pack_file_item in cls._pack_files if len(pack_file_item.error_history) > 0])

    @classmethod
    def _show_banner(cls):
        cls._banner = utils.read_file(cls._banner_path)
        [logger.info(info) for info in cls._banner.split('\n')]

    @classmethod
    @encircle_intercept(start_tip='加载配置开始', end_tip='加载配置完成')
    def _load_config(cls):
        cls._config = init_config(cls._config_path)
        # 设置日志等级
        logger.setLevel(cls._config.pack_global.log_level_obj.value)
        [logger.info(info) for info in str(cls._config).split('\n')]

    @classmethod
    @encircle_intercept(start_tip='加载密码表开始', end_tip='加载密码表完成')
    def _load_passwords(cls):
        password_line = utils.read_file(cls._config.pack_path.passwords).split('\n')
        # 默认添加无密码
        cls._passwords = {''}
        cls._passwords = cls._passwords.union(password_line)
        logger.info(f'[{",".join(cls._passwords)}]')

    @classmethod
    @duration_time(UnpackStat.scan_duration)
    @encircle_intercept(start_tip='压缩包扫描开始', end_tip='压缩包扫描完成')
    def _pack_scan(cls):
        for fa, _dirs, fs in os.walk(cls._config.pack_path.pack):
            logger.debug(f'开始扫描文件夹[{fa}],已发现文件[{len(fs)}]个')
            pack_file = [
                PackFile(name=name, path=fa, status=PackFileStatusEnum.SCAN, unpack_path=cls._config.pack_path.unpack)
                for name in fs
            ]
            [logger.debug(info) for info in pack_file]
            cls._pack_files.extend(pack_file)

            # 是否扫描子文件夹
            if not cls._config.pack_scan.is_deep_scan:
                logger.debug('已跳过扫描子文件夹')
                break

        logger.info(f'压缩包扫描成功收录:{len(cls._pack_files)}个文件')

    @classmethod
    @error_history(tip_msg="压缩包改名异常", error_status=PackFileStatusEnum.RENAME_FAIL)
    def _pack_rename_callback(cls, pack_file_item: PackFile):
        temp_name = pack_file_item.name

        for rule_item in cls._config.pack_rename.rule_chain_obj:
            new_name = temp_name
            if rule_item.module == PackRenameEnum.REPLACE:
                # 替换模式
                new_name = temp_name.replace(rule_item.replace_old, rule_item.replace_new)
            elif rule_item.module == PackRenameEnum.GROUP:
                # 捕获组模式
                new_name = re.sub(rule_item.group_pattern, rule_item.group_repl, temp_name)

            if new_name != temp_name:
                temp_name = new_name

        if temp_name.strip() == '':
            raise UnpackException(f'改名异常:无法将[{pack_file_item.name}]改为[{temp_name}]文件名不能为空')

        # 是否需要改名
        if pack_file_item.name != temp_name:
            # 改名异常抛出
            try:
                utils.rename_file(pack_file_item.path, pack_file_item.name, temp_name)
            except Exception as e:
                raise UnpackException(f'改名异常:无法将[{pack_file_item.name}]改为[{temp_name}] {e}')

            pack_file_item.status = PackFileStatusEnum.RENAME
            logger.info(pack_file_item)
        else:
            pack_file_item.status = PackFileStatusEnum.UN_RENAME
            logger.debug(pack_file_item)

    @classmethod
    @duration_time(UnpackStat.rename_duration)
    @encircle_intercept(
        lambda cls: cls._config.pack_rename.is_open, un_open_tip='[功能已关闭]压缩包改名',
        start_tip='压缩包改名开始', end_tip='压缩包改名完成'
    )
    def _pack_rename(cls):
        cls._each_file_by_status_callback(
            [
                PackFileStatusEnum.SCAN
            ],
            cls._pack_rename_callback
        )

    @classmethod
    @error_history(tip_msg="压缩包过滤异常", error_status=PackFileStatusEnum.FILTER_EXCLUDE)
    def _pack_filter_callback(cls, pack_file_item: PackFile):
        is_match = False

        for rule_item in cls._config.pack_filter.rule_chain_obj:
            # 包含模式
            if rule_item.module == PackFilterEnum.INCLUDE \
                    and not utils.is_re_match(rule_item.include_re, pack_file_item.name):
                break
            # 排除模式
            elif rule_item.module == PackFilterEnum.EXCLUDE \
                    and utils.is_re_match(rule_item.exclude_re, pack_file_item.name):
                break
        else:
            is_match = True

        pack_file_item.status = PackFileStatusEnum.FILTER_INCLUDE if is_match else PackFileStatusEnum.FILTER_EXCLUDE
        logger.info(pack_file_item)

    @classmethod
    @duration_time(UnpackStat.filter_duration)
    @encircle_intercept(
        lambda cls: cls._config.pack_filter.is_open, un_open_tip='[功能已关闭]压缩包过滤',
        start_tip='压缩包过滤开始', end_tip='压缩包过滤完成'
    )
    def _pack_filter(cls):
        # 处理以下状态的文件
        cls._each_file_by_status_callback(
            [
                PackFileStatusEnum.SCAN,
                PackFileStatusEnum.RENAME,
                PackFileStatusEnum.UN_RENAME
            ],
            cls._pack_filter_callback
        )

    @classmethod
    @error_history(tip_msg="压缩包识别异常", error_status=PackFileStatusEnum.ANALYSIS_FAIL)
    def _pack_analysis_callback(cls, pack_file_item: PackFile):
        for password in cls._passwords:
            logger.debug(f'尝试使用密码[{password}]识别:[{pack_file_item.name}]')

            analysis_res = Util7z.analysis(pack_file_item.get_file_full_path(), password)

            logger.debug(f'识别结果:{analysis_res}')

            if analysis_res.status == Util7zResCodeEnum.NO_ERROR:

                status = PackFileStatusEnum.ANALYSIS_SUCCESS

                # 分卷且子卷
                if analysis_res.analysis_info.is_split_item:
                    status = PackFileStatusEnum.ANALYSIS_SUCCESS_SPLIT

                # 识别成功
                pack_file_item.status = status
                # 记录识别信息
                pack_file_item.analysis_info = analysis_res.analysis_info
                break

        else:
            pack_file_item.status = PackFileStatusEnum.ANALYSIS_FAIL

        logger.info(pack_file_item)

    @classmethod
    @duration_time(UnpackStat.analysis_duration)
    @encircle_intercept(
        lambda cls: cls._config.pack_analysis.is_open, un_open_tip='[功能已关闭]压缩包识别',
        start_tip='压缩包识别开始', end_tip='压缩包识别完成'
    )
    def _pack_analysis(cls):
        pool = ThreadPool(cls._config.pack_analysis.thread_pool_max)

        # 处理以下状态的文件
        cls._each_file_by_status_callback(
            [
                PackFileStatusEnum.SCAN,
                PackFileStatusEnum.RENAME,
                PackFileStatusEnum.UN_RENAME,
                PackFileStatusEnum.FILTER_INCLUDE
            ],
            lambda item: pool.apply_async(cls._pack_analysis_callback, kwds={'pack_file_item': item})
        )

        pool.close()
        pool.join()

    @classmethod
    @error_history(tip_msg="压缩包测试异常", error_status=PackFileStatusEnum.TEST_FAIL)
    def _pack_test_callback(cls, pack_file_item: PackFile):
        # 调用 7zip 测试压缩包
        for password in cls._passwords:
            logger.debug(f'尝试用密码:[{password}]测试:[{pack_file_item.name}]')

            test_res = Util7z.test(pack_file_item.get_file_full_path(), password)

            logger.debug(f'测试结果:{test_res}')
            if test_res.status == Util7zResCodeEnum.NO_ERROR:
                pack_file_item.status = PackFileStatusEnum.TEST_SUCCESS
                pack_file_item.password = password
                break
        else:
            # 测试失败
            pack_file_item.status = PackFileStatusEnum.TEST_FAIL

        logger.info(pack_file_item)

    @classmethod
    @duration_time(UnpackStat.test_duration)
    @encircle_intercept(
        lambda cls: cls._config.pack_test.is_open, un_open_tip='[功能已关闭]压缩包测试',
        start_tip='压缩包测试开始', end_tip='压缩包测试完成'
    )
    def _pack_test(cls):
        pool = ThreadPool(cls._config.pack_test.thread_pool_max)

        # 处理以下状态的文件
        cls._each_file_by_status_callback(
            [
                PackFileStatusEnum.SCAN,
                PackFileStatusEnum.RENAME,
                PackFileStatusEnum.UN_RENAME,
                PackFileStatusEnum.FILTER_INCLUDE,
                PackFileStatusEnum.ANALYSIS_SUCCESS
            ],
            lambda item: pool.apply_async(cls._pack_test_callback, kwds={'pack_file_item': item})
        )

        pool.close()
        pool.join()

    @classmethod
    def _del_unpack(cls, pack_file_item: PackFile):
        # 是否识别过文件类型 成功/分卷
        is_analysis_success = pack_file_item.is_has_status(
            [PackFileStatusEnum.ANALYSIS_SUCCESS, PackFileStatusEnum.ANALYSIS_SUCCESS_SPLIT])

        # 未识别过压缩包类型
        if (not is_analysis_success) or (pack_file_item.analysis_info is None):
            logger.info(f'压缩包[{pack_file_item.name}]未识别/识别失败,暂不支持删除')
            return

        # 删除压缩包 (分卷压缩不支持删除)
        if pack_file_item.analysis_info.is_split:
            logger.info(f'压缩包[{pack_file_item.name}]为分卷压缩,暂不支持删除')
            return

        try:
            utils.remove_file(pack_file_item.get_file_full_path())
            pack_file_item.is_del = True
            logger.info(f'压缩包[{pack_file_item.name}]已删除')
        except Exception as e:
            logger.error(f'压缩包[{pack_file_item.name}]删除异常: {e}')

    @classmethod
    @error_history(tip_msg="压缩包解压异常", error_status=PackFileStatusEnum.UNPACK_FAIL)
    def _pack_unpack_callback(cls, pack_file_item: PackFile):

        parcel_unpack_file_obj = cls._config.pack_unpack.parcel_unpack_file_obj

        is_need_parcel = False

        if PackParcelUnpackFileEnum.ALWAYS == parcel_unpack_file_obj:
            # 总是
            is_need_parcel = True

        elif PackParcelUnpackFileEnum.AUTO == parcel_unpack_file_obj:
            # 自动
            # 判断压缩包是否是单文件

            if pack_file_item.is_has_status([PackFileStatusEnum.ANALYSIS_SUCCESS]):
                analysis_info = pack_file_item.analysis_info
                # 经过识别
                if cls._config.pack_unpack.is_keep_dir and analysis_info.root_file_count > 1:
                    # 保持解压层级关系 且 根目录文件数大于 1
                    is_need_parcel = True
                elif not cls._config.pack_unpack.is_keep_dir and analysis_info.file_list_count > 1:
                    # 不保持解压层级关系 且 文件数大于 1
                    is_need_parcel = True
            else:
                # 未识别
                is_need_parcel = True

        elif PackParcelUnpackFileEnum.NEVER == parcel_unpack_file_obj:
            # 从不
            pass

        if is_need_parcel:
            # 保证包裹文件夹唯一性(添加uuid后缀)
            parcel_name = f'{pack_file_item.name}_{utils.create_uuid()}'

            pack_file_item.unpack_path = utils.path_join(pack_file_item.unpack_path, parcel_name)

        passwords = cls._passwords

        # 未经过测试则需要遍历密码表
        if pack_file_item.is_has_password:
            passwords = [pack_file_item.password]

        for password in passwords:
            logger.debug(f'尝试用密码:[{password}]解压:[{pack_file_item.name}]')

            unpack_res = Util7z.unpack(file_path=pack_file_item.get_file_full_path(),
                                       password=password,
                                       unpack_path=pack_file_item.unpack_path,
                                       overwrite_model=cls._config.pack_unpack.overwrite_model_obj.value,
                                       is_keep_dir=cls._config.pack_unpack.is_keep_dir)

            logger.debug(f'解压结果如下:{unpack_res}')

            if unpack_res.status == Util7zResCodeEnum.NO_ERROR:
                # 解压成功
                pack_file_item.status = PackFileStatusEnum.UNPACK_SUCCESS
                # 回写密码
                pack_file_item.password = password
                # 删除解压成功的压缩包
                if cls._config.pack_unpack.is_success_del:
                    cls._del_unpack(pack_file_item)
                break
        else:
            # 解压失败
            pack_file_item.status = PackFileStatusEnum.UNPACK_FAIL

        logger.info(pack_file_item)

    @classmethod
    @duration_time(UnpackStat.unpack_duration)
    @encircle_intercept(
        lambda cls: cls._config.pack_unpack.is_open, un_open_tip='[功能已关闭]压缩包解压',
        start_tip='压缩包解压开始', end_tip='压缩包解压完成'
    )
    def _pack_unpack(cls):
        pool = ThreadPool(cls._config.pack_unpack.thread_pool_max)

        # 处理以下状态的文件
        cls._each_file_by_status_callback(
            [
                PackFileStatusEnum.SCAN,
                PackFileStatusEnum.RENAME,
                PackFileStatusEnum.UN_RENAME,
                PackFileStatusEnum.FILTER_INCLUDE,
                PackFileStatusEnum.TEST_SUCCESS,
                PackFileStatusEnum.ANALYSIS_SUCCESS
            ],
            lambda item: pool.apply_async(cls._pack_unpack_callback, kwds={'pack_file_item': item})
        )

        pool.close()
        pool.join()

    @classmethod
    @duration_time(UnpackStat.clear_duration)
    @encircle_intercept(
        lambda cls: cls._config.pack_clear.is_open, un_open_tip='[功能已关闭]压缩包清理',
        start_tip='压缩包清理开始', end_tip='压缩包清理完成'
    )
    def _pack_clear(cls):
        # 删除压缩包存放文件夹中的空文件夹
        if cls._config.pack_clear.is_del_pack_empty_folder:
            _, del_count = utils.del_empty_folder(cls._config.pack_path.pack)
            logger.info(f'删除压缩包存放文件夹中的空文件夹完成:{del_count}')

        # 删除压缩包解压存放文件夹中的空文件夹
        if cls._config.pack_clear.is_del_unpack_empty_folder:
            _, del_count = utils.del_empty_folder(cls._config.pack_path.unpack)
            logger.info(f'删除压缩包解压存放文件夹中的空文件夹完成:{del_count}')

    @classmethod
    def _pack_report(cls):
        UnpackStat.scan_count = cls._count_status_history([PackFileStatusEnum.SCAN])
        UnpackStat.rename_count = cls._count_status_history([PackFileStatusEnum.RENAME])
        UnpackStat.filter_exclude_count = cls._count_status_history([PackFileStatusEnum.FILTER_EXCLUDE])
        UnpackStat.analysis_fail_count = cls._count_status_history([PackFileStatusEnum.ANALYSIS_FAIL])
        UnpackStat.analysis_success_split_count = cls._count_status_history([PackFileStatusEnum.ANALYSIS_SUCCESS_SPLIT])
        UnpackStat.test_fail_count = cls._count_status_history([PackFileStatusEnum.TEST_FAIL])
        UnpackStat.unpack_fail_count = cls._count_status_history([PackFileStatusEnum.UNPACK_FAIL])
        UnpackStat.unpack_success_count = cls._count_status_history([PackFileStatusEnum.UNPACK_SUCCESS])
        UnpackStat.unpack_error_count = cls._count_error_history()

        report_infos = [cls._banner]

        if cls._config.pack_report.is_show_config:
            report_infos.append(utils.title_format('配置信息', 100, '=', f'{cls._config}'))

        if cls._config.pack_report.is_show_status:
            report_infos.append(utils.title_format('统计信息', 100, '=', f'{UnpackStat.get_status_info()}'))

        if cls._config.pack_report.is_show_pack_info:
            pack_file = []
            # 排序 分组
            cls._pack_files.sort(key=lambda x: x.status.name)
            pack_file_group = groupby(cls._pack_files, key=lambda x: x.status.name)
            # 按需求显示
            for key, group in pack_file_group:
                if str(key).lower() in cls._config.pack_report.show_pack_status:
                    pack_file.extend([str(item) for item in group])
                    pack_file.append('')

            report_infos.append(utils.title_format('详细信息', 100, '=', *pack_file))

        utils.write_file(cls._config.pack_path.report, '\n'.join(report_infos))
        logger.info(f'详细统计信息见: {cls._config.pack_path.report}')

    @classmethod
    def _pack_error(cls):
        is_has_error = False
        for item in cls._pack_files:
            if item.is_has_error:
                logger.error(f'压缩包处理异常:{item}')
                is_has_error = True

        if is_has_error:
            logger.error('处理流程存在异常')
        else:
            logger.info('处理流程不存在异常')

    @classmethod
    def _run_auto_unpack(cls):
        # 显示banner
        cls._show_banner()
        # 加载配置
        cls._load_config()
        # 加载密码表
        cls._load_passwords()
        # 压缩包扫描
        cls._pack_scan()
        # 压缩包改名
        cls._pack_rename()
        # 压缩包过滤
        cls._pack_filter()
        # 压缩包识别
        cls._pack_analysis()
        # 压缩包测试
        cls._pack_test()
        # 压缩包解压
        cls._pack_unpack()
        # 压缩包清理
        cls._pack_clear()
        # 显示处理压缩包过程中的异常
        cls._pack_error()
        # 生成解压报告
        cls._pack_report()

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
