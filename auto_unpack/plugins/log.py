import logging
from datetime import datetime
from typing import Any, Callable, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

from auto_unpack.plugin import OutputPluginConfig, Plugin
from auto_unpack.store import Context, FileData
from auto_unpack.util.file import get_next_not_exist_path, write_file

logger = logging.getLogger(__name__)


class LogPluginConfig(OutputPluginConfig):
    """
    日志插件配置
    """

    name: Literal["log"] = Field(default="log", description="日志插件")
    file_name: str = Field(default="log", description="日志文件名(默认: log)")
    print_stats: List[Literal["all", "ctime", "mtime", "size"]] = Field(
        default=[],
        description="打印文件信息(默认: [])\n'all'：所有信息\n'ctime'：创建时间\n'mtime'：修改时间\n'size'：文件大小",
    )


class LogFileStat(BaseModel):
    """
    文件信息
    """

    ctime: str = Field(default=None, description="创建时间")
    mtime: str = Field(default=None, description="修改时间")
    size: int = Field(default=None, description="文件大小(单位: 字节)")


class LogFileData(FileData):
    """
    文件数据
    """

    stat: Optional[LogFileStat] = Field(default=None, description="文件信息")


class LogContext(Context):
    """
    日志类
    """

    file_datas: List[LogFileData] = Field(default=[], description="文件数据")


class LogPlugin(Plugin[LogPluginConfig]):
    """
    日志插件

    作用: 上下文信息保存到文件
    """

    name: str = "log"

    def _timestamp_to_str(self, timestamp: float) -> str:
        """
        时间戳转字符串
        """
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

    def _file_data_to_log_file_data(self, file_data: FileData) -> LogFileData:
        """
        转换文件数据为日志文件数据
        """
        file_info = LogFileStat()

        stat_map: Dict[str, Callable[[FileData], Any]] = {
            "ctime": lambda x: self._timestamp_to_str(x.path.stat().st_ctime),
            "mtime": lambda x: self._timestamp_to_str(x.path.stat().st_mtime),
            "size": lambda x: x.path.stat().st_size,
        }

        if "all" in self.config.print_stats:
            for stat in stat_map.keys():
                file_info = file_info.model_copy(
                    update={stat: stat_map[stat](file_data)}
                )
        else:
            for stat in self.config.print_stats:
                if stat in stat_map.keys():
                    file_info = file_info.model_copy(
                        update={stat: stat_map[stat](file_data)}
                    )

        return LogFileData(
            path=file_data.path, search_path=file_data.search_path, stat=file_info
        )

    def _context_to_log_context(self, context: Context) -> LogContext:
        """
        转换上下文信息为文件数据
        """
        if len(self.config.print_stats) == 0:
            return LogContext(
                file_datas=[
                    LogFileData(path=f.path, search_path=f.search_path, stat=None)
                    for f in context.file_datas
                ]
            )

        return LogContext(
            file_datas=[self._file_data_to_log_file_data(f) for f in context.file_datas]
        )

    def execute(self):
        context = self.load_context()

        log_path = get_next_not_exist_path(
            self.global_config.info_dir / f"{self.config.file_name}.json"
        )

        log_context = self._context_to_log_context(context)

        write_file(log_path, log_context.model_dump_json(indent=2, exclude_none=True))

        logger.info(f"Log file data saved to {log_path}")
