from functools import wraps
from flask import request, abort, current_app
from enum import Enum


class APIKey(Enum):
    PLATFORM = "platform"
    SOLID = "solid"
    GENERAL = "general"


def validate_api_key(key_enum):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            api_key = request.headers.get("x-api-key")

            if not api_key:
                abort(401, description="Missing api_key")

            # Replace this with your actual key validation logic
            valid_keys = {
                APIKey.PLATFORM: current_app.config["api_key_backend_platform_in"],
                # APIKey.SOLID: current_app.config["solid_key"],
                # APIKey.GENERAL: current_app.config["general_key"],
            }
            if api_key != valid_keys[key_enum]:
                abort(403, description="Invalid api_key")

            return func(*args, **kwargs)

        return wrapper

    return decorator
