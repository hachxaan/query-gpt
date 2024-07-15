import logging
import socket


class HostnameFilter(logging.Filter):
    hostname = socket.gethostname()

    def __init__(self, environment):
        super().__init__()
        self.environment = environment

    def filter(self, record):
        record.hostname = HostnameFilter.hostname
        record.environment = self.environment
        return True
