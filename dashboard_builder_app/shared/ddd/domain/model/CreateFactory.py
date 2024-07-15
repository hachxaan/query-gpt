from abc import ABCMeta


class CreateFactory(metaclass=ABCMeta):

    __create_key = object()

    def __init__(self, create_key):
        assert(
            create_key == self.__create_key), \
            f"{type(self).__name__} objects must be created using \
                    {type(self).__name__}.of([args])"

    @classmethod
    def _create(cls):
        return cls(cls.__create_key)
