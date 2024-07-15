import json
import traceback
from typing import Dict

from flask import jsonify, request
from src.shared.tools.errors.project_exception import ProjectException
from src.shared.tools.auth.access import decode_from_token


def get_error_with_exception(exception):
    return exception.serialize


def log_trace_if_needed(exception, logger):
    if exception.show_trace is True:
        logger.exception(get_log_dict(exception))
    else:
        logger.warning(get_log_dict(exception.serialize))


def constructor_error_handler(logger):
    def send_error(exception):
        if isinstance(exception, ProjectException):
            error = get_error_with_exception(exception)
            log_trace_if_needed(exception=exception, logger=logger)
            return jsonify(error), int(error['code']), {'Server': ''}

        trace = traceback.format_exc()
        exception = ProjectException(tag='INTERNAL_ERROR', trace=trace)
        error = get_error_with_exception(exception)
        logger.exception(get_log_dict(error))
        return jsonify(error), int(error['code']), {'Server': ''}

    return send_error


def get_user_id():
    token = request.headers.get('Authorization')

    if token is not None:
        user_info = decode_from_token(token=token)
        return user_info['id']
    else:
        raise Exception


def get_values_from_marshmallow_error(error: Dict):
    starting_string = 'An error occurred with input: '
    if error['message'].startswith(starting_string):
        message = error['message'].strip(starting_string)
        message_dict = json.loads(message.replace("\'", "\""))
        keys = message_dict.keys()
        return {key: request.json[key] for key in keys}
    else:
        raise Exception


def get_log_dict(error):
    log_dict = dict(error=error)
    try:
        log_dict['user_id'] = get_user_id()
    except Exception:
        pass
    try:
        log_dict['method'] = request.method
    except Exception:
        pass
    try:
        log_dict['values'] = get_values_from_marshmallow_error(error)
    except Exception:
        pass

    return log_dict
