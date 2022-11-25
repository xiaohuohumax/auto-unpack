import logging
from pathlib import Path

from .result import Util7zUnpackRes, Util7zTestRes, Util7zAnalysisRes
from .utils import run_cmd

logger = logging.getLogger()


class Util7z(object):
    """
    7zip 工具
    """

    lib7zip_path: str = str(Path(Path(__file__).parent, 'lib7zip/7z.exe'))

    @classmethod
    def unpack(cls, file_path: str, password: str = '', unpack_path: str = '', overwrite_model: str = 't',
               is_keep_dir: bool = True) -> Util7zUnpackRes:
        """
        解压压缩包

        命令: 7z.exe x/e "file" -y -ao[a/s/t/u] -o"output_path" -p"password"
        :param file_path: 压缩包存放路径
        :param password: 密码
        :param unpack_path: 解压路径
        :param overwrite_model: 覆盖模式 a/s/t/u
        :param is_keep_dir: 是否保持解压文件层级关系
        :return: 解压结果
        """
        cmd_list = [
            cls.lib7zip_path,
            'x' if is_keep_dir else 'e',
            f'"{file_path}"',
            '-y',
            f'-ao{overwrite_model}',
            f'-o"{unpack_path}"',
            f'-p"{password}"'
        ]
        logger.debug(' '.join(cmd_list))
        return Util7zUnpackRes(*run_cmd(cmd_list))

    @classmethod
    def test(cls, file_path: str, password: str = '') -> Util7zTestRes:
        """
        测试压缩包

        命令: 7z.exe t "file" -p"password" -y
        :param file_path: 压缩包存放路径
        :param password: 密码
        :return: 测试结果
        """
        cmd_list = [
            cls.lib7zip_path,
            't',
            f'"{file_path}"',
            f'-p"{password}"',
            '-y'
        ]
        logger.debug(' '.join(cmd_list))
        return Util7zTestRes(*run_cmd(cmd_list))

    @classmethod
    def analysis(cls, file_path: str, password: str = '') -> Util7zAnalysisRes:
        """
        识别压缩包

        命令: 7z.exe l "file" -p"password" -y
        :param file_path: 压缩包存放路径
        :param password: 密码
        :return: 识别结果
        """
        cmd_list = [
            cls.lib7zip_path,
            'l',
            f'"{file_path}"',
            f'-p"{password}"',
            '-y'
        ]
        logger.debug(' '.join(cmd_list))
        return Util7zAnalysisRes(*run_cmd(cmd_list))
