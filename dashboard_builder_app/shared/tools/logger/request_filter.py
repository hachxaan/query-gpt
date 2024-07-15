import logging

from flask import has_request_context, request


class RequestFilter(logging.Filter):
    def filter(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.headers.get('X-Real-IP')
        else:
            record.url = None
            record.remote_addr = None
        return True
