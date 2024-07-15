from flask import jsonify
from src.shared.tools.errors.project_exception import ProjectException
from src.shared.tools.errors.error_handler import get_error_with_exception
from src.shared.tools.logger import internal_logger


logger = internal_logger.get_logger()


def send_not_found(_):
    exception = ProjectException(tag='NOT_FOUND')
    error = get_error_with_exception(exception)
    logger.info(exception.serialize)
    return jsonify(error), int(error['code']), {'Server': ''}
