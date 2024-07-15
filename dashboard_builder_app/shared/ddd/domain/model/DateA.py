from datetime import datetime

from .helpers.DateHelper import DateHelper
from .ValueObject import ValueObject


class DateException(Exception):  # TODO: Pasar a exception de Dominio
    """A base class for all business rule validation exceptions"""


class DateA(ValueObject):

    __create_key = object()

    def __init__(self, create_key, value):
        super().__init__(value)
        assert (
            create_key == DateA.__create_key), \
            f"{type(self).__name__} \
                objects must be created using {type(self).__name__}.of([args])"

    @classmethod
    def __create(cls, value) -> 'DateA':
        return DateA(cls.__create_key, value)

    @staticmethod
    def create() -> 'DateA':
        return DateA.__create(DateHelper.of().generate())

    @staticmethod
    def ofString(value: str) -> 'DateA':
        if DateHelper.of().validate(value):
            return DateA.__create(value)
        else:
            raise DateException(
                'Date string invalid. Required format: "YYYY-MM-DD"')

    @staticmethod
    def ofDateTime(value: datetime) -> 'DateA':
        return DateA.__create(value)

    def equals(self, date: 'DateA') -> bool:
        return date.value == self.value

    @property
    def value(self):
        return self._value

    @classmethod
    def getString(self) -> str:
        return self.value  # .strftime('YYYY-mm-dd')
