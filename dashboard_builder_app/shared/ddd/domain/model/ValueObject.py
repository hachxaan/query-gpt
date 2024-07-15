
import abc
from typing import Any


class ValueObject(metaclass=abc.ABCMeta):

    def __init__(self, value):
        self._value = value

    @abc.abstractmethod
    def equals(self, value: Any) -> bool:
        pass

    @property
    def value(self):
        return self._value

    def __eq__(self, other):
        return self._value == other.value
