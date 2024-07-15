import logging

from logging.handlers import SysLogHandler
from flask_log_request_id import RequestIDLogFilter
from src.shared.tools.logger.formatter import console_formatter_papertrail_pattern
from src.shared.tools.logger.hostname_filter import HostnameFilter
from src.shared.tools.logger.request_filter import RequestFilter


def construct_papertrail(prefix, address, port, disabled=None):
    if disabled is not None and "False" in disabled:
        console_formatter = logging.Formatter(
            console_formatter_papertrail_pattern, datefmt='%b %d %H:%M:%S')

        papertrail_handler = SysLogHandler(address=(address, port))
        papertrail_handler.addFilter(HostnameFilter(environment=prefix))
        papertrail_handler.addFilter(RequestIDLogFilter())
        papertrail_handler.addFilter(RequestFilter())
        papertrail_handler.setFormatter(console_formatter)

        return papertrail_handler
    return None
