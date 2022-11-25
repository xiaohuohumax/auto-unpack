import logging
import logging.config
from logging import Formatter, StreamHandler
from logging.handlers import RotatingFileHandler


def init_logger(filename: str, level: int = logging.DEBUG):
    root = logging.getLogger()
    define_format = Formatter(fmt='%(asctime)s %(levelname)-10s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    file_handler = RotatingFileHandler(filename=filename, maxBytes=1024 * 1024 * 1024, backupCount=3, encoding='UTF-8')
    file_handler.setFormatter(define_format)

    console_handler = StreamHandler()
    console_handler.setFormatter(define_format)

    root.addHandler(file_handler)
    root.addHandler(console_handler)
    root.setLevel(level)

    return root


logger = init_logger('./unpack.log')

if __name__ == '__main__':
    logger.debug("debug")
    logger.info("info")
    logger.warning("warning")
    logger.error("error")
    logger.critical("critical")
