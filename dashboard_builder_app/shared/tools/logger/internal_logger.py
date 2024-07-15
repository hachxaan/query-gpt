import logging
import sys

from flask_log_request_id import RequestIDLogFilter

from src.shared.tools.logger.formatter import console_formatter_pattern
from src.shared.tools.logger.request_filter import RequestFilter
from src.shared.tools.logger.hostname_filter import HostnameFilter


def construct_logger(name, level, disabled, papertrail_handler=None):
    format = console_formatter_pattern
    logger = logging.getLogger('root')
    level = logging.getLevelName(level.upper())

    console_formatter = logging.Formatter(format, datefmt='%b %d %H:%M:%S')
    console = logging.StreamHandler(stream=sys.stdout)
    console.addFilter(RequestIDLogFilter())
    console.addFilter(RequestFilter())
    console.addFilter(HostnameFilter(environment=name))
    console.setFormatter(console_formatter)

    logger.addHandler(console)
    logger.setLevel(level)

    logger.info('Logger set with level %s' % logging.getLevelName(level))

    # Disable logger if needed (For example, for testing purposes)
    if disabled == "True":
        logger.disabled = True
        logger.info('Logger is deactivated')
    else:
        logger.info('Logger is activated')

        # Papertrail handler
        if papertrail_handler is not None:
            logger.addHandler(papertrail_handler)
            logger.info('Papertrail is activated')
        else:
            logger.info('Papertrail is deactivated')

    return logger


def get_logger():
    return logging.getLogger('root')
