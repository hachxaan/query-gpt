# backoffice/utils.py

from backoffice.middlewares.user_middleware import get_current_user


def get_current_user_id():
    user = get_current_user()
    if user and user.is_authenticated:
        return user.id
    return None


def get_session_user():
    user = get_current_user()
    if user and user.is_authenticated:
        return user
    return None