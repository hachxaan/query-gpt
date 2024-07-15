from typing import Dict, Tuple

import jwt
from flask import current_app

from src.config.constants import (
    SALT_KEY_NAME, BEARER_STRING_NAME, TOKEN_TIMEOUT_NAME
)
from src.shared.tools.logger import internal_logger
from src.shared.tools.errors.project_exception import ProjectException
from .redis import RedisSingleton


logger = internal_logger.get_logger()


class WhiteList:
    def __init__(self):
        self.whitelist = RedisSingleton.instance

    def set(self, _id: int, token: str):
        self.whitelist.set(_id, token)

    def __getitem__(self, _id: int):
        return self.whitelist.get(_id)

    def __setitem__(self, _id: int, token: str):
        timeout = current_app.config[TOKEN_TIMEOUT_NAME]
        self.whitelist.set(_id, token, ex=timeout)

    def pop(self, token: str):
        decoded, token = self.decode(token)
        if decoded:
            self.whitelist.delete(decoded['id'])

    def __contains__(self, token: str) -> bool:
        result = False
        decoded, token = self.decode(token)

        if decoded:
            stored_token = self.whitelist.get(decoded['id'])
            if stored_token is not None:
                stored_token = stored_token.decode(encoding='UTF-8')
                result = stored_token and stored_token == token

        return result

    @staticmethod
    def decode(token: str) -> Tuple[Dict, str]:
        decoded = None
        if token.startswith(BEARER_STRING_NAME):
            token = token[len(BEARER_STRING_NAME):]
            _, key = current_app.config[SALT_KEY_NAME]

            try:
                decoded = jwt.decode(token, key, algorithms='HS256')
            except jwt.exceptions.DecodeError as exc:
                raise ProjectException(tag="NOT_AUTH") from exc
            except jwt.ExpiredSignatureError as exc:
                raise ProjectException(tag="EXPIRED_TOKEN") from exc

        return decoded, token
