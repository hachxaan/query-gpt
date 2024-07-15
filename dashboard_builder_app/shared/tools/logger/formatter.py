console_formatter_pattern = " [%(asctime)s %(hostname)s %(environment)s %(levelname)s - " \
                            "request_id=%(request_id)s url=%(url)s remote_address=%(remote_addr)s - %(message)s "

console_formatter_papertrail_pattern = "%(asctime)s %(hostname)s %(environment)s %(levelname)s - " \
                                       "request_id=%(request_id)s url=%(url)s remote_address=%(remote_addr)s - " \
                                       "%(message)s "
