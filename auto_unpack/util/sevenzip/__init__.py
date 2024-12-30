import logging
import platform
from pathlib import Path
from typing import List, TypeVar

from ..exec import exec_cmd
from .result import ExtractResult, ListResult, Result, ResultCode, TestResult

logger = logging.getLogger(__name__)


T = TypeVar("T", bound=Result)


def load_sevenzip_lib() -> Path:
    """
    加载 7zip 库


    :return: 7zip 库路径
    """
    lib_path = Path(__file__).parent / "lib"

    # 系统
    system = platform.system().lower()
    system_path = lib_path / system
    if not system_path.exists():
        raise NotImplementedError(f"Platform not supported: {system}")

    # 处理器
    machine = platform.machine().lower()
    machine_map = {"amd": "amd", "arm": "arm", "x86_64": "amd"}

    machine_name = next((v for k, v in machine_map.items() if k in machine), "")
    machine_path = system_path / machine_name
    if machine_name == "" or not machine_path.exists():
        raise NotImplementedError(f"Machine not supported: {machine}")

    # 位数
    architecture = platform.architecture()[0].lower()
    architecture_map = {"64bit": "x64", "32bit": "x86", "arm64": "x64", "arm32": "x86"}

    architecture_name = architecture_map.get(architecture, "")
    architecture_path = machine_path / architecture_name
    if architecture_name == "" or not architecture_path.exists():
        raise NotImplementedError(f"Architecture not supported: {architecture}")

    # 7zip 可执行文件
    bin_map = {"windows": "7z.exe", "linux": "7zzs", "darwin": "7zz"}
    bin_name = bin_map.get(system, "")
    bin_path = architecture_path / bin_name
    if bin_name == "" or not bin_path.exists():
        raise NotImplementedError(f"System not supported: {system}")

    try:
        # 部分环境下, 7zip 权限不够, 需要 chmod 755
        bin_path.chmod(0o755)
    except Exception as e:
        logger.warning(f"chmod 755 {bin_path} failed: {e}")

    logger.debug(f"7zip lib path: {bin_path}")
    return bin_path


class SevenZipUtil:
    """
    7zip 工具类
    """

    # 7zip 可执行文件路径
    # todo: 更改为动态下载库文件，并且添加自定义路径功能
    _lib_path: Path = load_sevenzip_lib()

    @classmethod
    def handle_result_code(self, code: int, message: str) -> ResultCode:
        """
        处理 7-zip 扩展状态码

        :param code: 返回码
        :param message: 返回信息
        :return: 状态码
        """
        result_code = ResultCode.init(code)
        if result_code == ResultCode.NO_ERROR:
            return result_code

        keyword_map = {"Headers Error in encrypted archive.": ResultCode.HEADERS_ERROR}

        for k, c in keyword_map.items():
            if k in message:
                return c

        return result_code

    @classmethod
    def exec(
        cls,
        sub: str,
        options: List[str],
        file_path: Path,
        password: str = "",
        result_class: T = Result,
    ) -> T:
        """
        执行 7zip 命令

        :param sub: 子命令
        :param options: 命令选项
        :param file_path: 压缩包路径
        :param password: 密码
        :param result_class: 结果类
        :return: 结果
        """
        cmds = [
            f'"{str(cls._lib_path)}"',
            sub,
            f'"{file_path}"',
            f'-p"{password}"',
            "-y",
            *options,
        ]
        code, message = exec_cmd(cmds)
        result_code = cls.handle_result_code(code, message)
        return result_class(
            message=message, file_path=file_path, password=password, code=result_code
        )

    @classmethod
    def extract(
        cls,
        file_path: Path,
        password: str = "",
        output_dir: Path = "",
        overwrite: str = "t",
        keep_dir: bool = True,
    ) -> ExtractResult:
        """
        解压 7zip 压缩包

        :param file_path: 压缩包路径
        :param password: 密码
        :param output_dir: 输出目录
        :param overwrite: 覆盖模式 a/s/t/u
        :param keep_dir: 是否保留目录结构
        :return: 解压结果
        """
        sub = "x" if keep_dir else "e"
        options = [
            f"-ao{overwrite}",
            f'-o"{output_dir}"',
        ]
        return cls.exec(sub, options, file_path, password, ExtractResult)

    @classmethod
    def list(cls, file_path: Path, password: str = "") -> ListResult:
        """
        列出 7zip 压缩包信息

        :param file_path: 压缩包路径
        :param password: 密码
        :return: 压缩包信息
        """
        return cls.exec("l", [], file_path, password, ListResult)

    @classmethod
    def test(cls, file_path: Path, password: str = "") -> TestResult:
        """
        测试 7zip 压缩包是否完整

        :param file_path: 压缩包路径
        :param password: 密码
        :return: 测试结果
        """
        return cls.exec("t", [], file_path, password, ListResult)
