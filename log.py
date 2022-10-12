import logging.config

config = {
    'version': 1,
    'disable_existing_loggers': True,
    'incremental': False,
    'formatters':
        {
            'define_format': {
                'class': 'logging.Formatter',
                'format': '%(asctime)s %(levelname)-10s: %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
    'handlers':
        {
            'define_console_handler': {
                'class': 'logging.StreamHandler',
                'level': logging.DEBUG,
                'formatter': 'define_format',
            },
            'define_file_handler': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': logging.INFO,
                'formatter': 'define_format',
                'filename': './unpack.log',
                'maxBytes': 1024 * 1024,
                'backupCount': 3,
                'encoding': 'UTF-8',
            },

        },

    'root':
        {
            'handlers': ['define_console_handler', 'define_file_handler'],
            'level': logging.DEBUG,
        },

}

logging.config.dictConfig(config)

logger = logging.getLogger()
only_logger = logging.getLogger('only')

if __name__ == '__main__':
    logger.debug("debug")
    logger.info("info")
    logger.warning("warning")
    logger.error("error")
    logger.critical("critical")
