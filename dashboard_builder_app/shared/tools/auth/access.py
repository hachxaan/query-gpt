from functools import wraps
from typing import Callable, Dict
from flask import abort, current_app, request


from src.config.constants import SMS_CODE_HEADER_NAME
from src.shared.adapters.backen_platform_adapter import BackendPlatformAdapter
from src.shared.cache.whitelist import WhiteList
from src.shared.services.user_service import UserService

from src.shared.tools.errors.project_exception import ProjectException
from src.shared.tools.logger import internal_logger

logger = internal_logger.get_logger()



def login_required(
    user_info: bool = False, second_factor_required: bool = False
) -> Callable:
    """
    Return the user of the token if a token exists and the decoded token is valid
    :param user_info:
    :param second_factor_required:
    :return:
    """

    def login_required_callable(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Callable:
            token = request.headers.get("Authorization")

            if token is None or not is_user_logged(token=token):
                raise ProjectException(tag="NOT_AUTH")
            user_info_token = decode_from_token(token=token)

            if user_info or second_factor_required:

                backend_adapter = BackendPlatformAdapter()
                user_service = UserService(backend_adapter)
                sms_code = request.headers.get(SMS_CODE_HEADER_NAME, None)
                user_response = user_service.get_user_minimal(
                    user_id=user_info_token["id"],
                    sms_code=sms_code
                )

                if second_factor_required:
                    if SMS_CODE_HEADER_NAME not in request.headers:
                        raise ProjectException(tag="SMS_CODE_NEEDED")

                    code = user_response.get('code')
                    data = user_response.get('data')
                    if code != 200:
                        if code == 404:
                            raise ProjectException(
                                tag='VERIFICATION_SMS_NOT_FOUND')
                        else:
                            raise ProjectException(tag=user_response.get(
                                'tag'), message=user_response.get('message'))
                    elif code == 200:
                        if data:
                            if not data.get('is_sms_code_valid'):
                                raise ProjectException(tag="INVALID_CODE")
                        else:
                            raise ProjectException(
                                tag="SMS_CODE_NOT_YET_VERIFIED")

                if user_info:
                    return func(user_response, *args, **kwargs)
            else:
                return func({'data': {'id': user_info_token["id"]}}, *args, **kwargs)
            return func(*args, **kwargs)

        return wrapper

    return login_required_callable


def api_key(
    user_info: str = 'platform'
) -> Callable:
    """
    Validate Api Key
    """

    def api_key_callable(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Callable:
            user_id = request.view_args.get('user_id')

            token = request.headers.get("x-api-key")

            if token is None or not is_user_logged(token=token):
                raise ProjectException(tag="NOT_AUTH")
            user_info_token = decode_from_token(token=token)

            if user_info or second_factor_required:

                backend_adapter = BackendPlatformAdapter()
                user_service = UserService(backend_adapter)
                sms_code = request.headers.get(SMS_CODE_HEADER_NAME, None)
                user_response = user_service.get_user_minimal(
                    user_id=user_info_token["id"],
                    sms_code=sms_code
                )

                if second_factor_required:
                    if SMS_CODE_HEADER_NAME not in request.headers:
                        raise ProjectException(tag="SMS_CODE_NEEDED")

                    code = user_response.get('code')
                    data = user_response.get('data')
                    if code != 200:
                        if code == 404:
                            raise ProjectException(
                                tag='VERIFICATION_SMS_NOT_FOUND')
                        else:
                            raise ProjectException(tag=user_response.get(
                                'tag'), message=user_response.get('message'))
                    elif code == 200:
                        if data:
                            if not data.get('is_sms_code_valid'):
                                raise ProjectException(tag="INVALID_CODE")
                        else:
                            raise ProjectException(
                                tag="SMS_CODE_NOT_YET_VERIFIED")

                if user_info:
                    return func(user_response, *args, **kwargs)
            else:
                return func({'data': {'id': user_info_token["id"]}}, *args, **kwargs)
            return func(*args, **kwargs)

        return wrapper

    return api_key


def is_user_logged(token) -> bool:
    """
    Check if user is logged
    :param token:
    :return bool:
    """
    return token in WhiteList()


def decode_from_token(token: str) -> Dict:
    """
    Return the decoded info in the token
    :param token:
    :return Dict:
    """
    return WhiteList.decode(token=token)[0]


def ip_whitelist(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        real_ip = request.headers.get('X-Real-IP', request.remote_addr)
        ip_whitelist = current_app.config.get('IP_WHITE_LIST_RIA', '').split(',')
        debug_api(f"real_ip: {real_ip}")
        debug_api(f"ip_whitelist: {ip_whitelist}")
        if real_ip not in ip_whitelist:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def api_key_ria(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('x-api-key')
        ria_api_key = current_app.config.get('X_API_KEY_RIA')
        debug_api(f"api_key: {api_key}")
        debug_api(f"ria_api_key: {ria_api_key}")        
        if api_key != ria_api_key:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def debug_api(message: str):
    if current_app.config.get('DEBUG_API_HEADER'):
        logger.info(message)