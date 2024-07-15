from typing import Set

from .redis import RedisSingleton


def cache(func):
    """
        Decorator to cache functions result in redis
    """

    def wrapper(*args, **kwargs):
        redis = RedisSingleton.instance
        _key = f'{func.__module__}.{func.__name__}'
        if args:
            _key += str(hash(args))
        if kwargs:
            _key += str(hash(kwargs.keys()))
            _key += str(hash(kwargs.values()))

        key = hash(_key)

        past_value = redis.get(key)
        if past_value is not None:
            return past_value.decode('utf-8')
        else:
            new_value = func(*args, **kwargs)
            redis.set(key, new_value)
            ClearableKeys().add(key)
            return new_value

    return wrapper


def cache_clear():
    ClearableKeys().clear()


class ClearableKeys:
    KEY = 'CLEARABLEKEYSKEY'

    @classmethod
    def get_set(cls) -> Set:
        bstr_value = RedisSingleton.instance.get(cls.KEY)
        if bstr_value is None:
            args = tuple()
        else:
            args = bstr_value.decode('utf-8').split(';')

        return set(args)

    @classmethod
    def add(cls, element):
        _set = cls.get_set()
        _set.add(str(element))
        RedisSingleton.instance.set(cls.KEY, ';'.join(_set))

    @classmethod
    def __iter__(cls):
        for element in cls.get_set():
            yield int(element)

    @classmethod
    def clear(cls):
        for key in cls():
            RedisSingleton.instance.delete(key)

        RedisSingleton.instance.delete(cls.KEY)
