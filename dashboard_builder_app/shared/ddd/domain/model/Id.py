from ..model.helpers.UuidHelper import UuidHelper
from .ValueObject import ValueObject


class UUIDException(Exception):  # TODO: Pasar a exception de Dominio
    """A base class for all business rule validation exceptions"""


class Id(ValueObject):

    __create_key = object()

    def __init__(self, create_key, value):
        super().__init__(value)
        assert (
            create_key == Id.__create_key), f"{type(self).__name__} \
              objects must be created using {type(self).__name__}.of([args])"

    @classmethod
    def __create(cls, value) -> 'Id':
        return Id(cls.__create_key, value)

    @staticmethod
    def create() -> 'Id':
        return Id.__create(UuidHelper.of().generate())

    @staticmethod
    def ofString(value: str) -> 'Id':
        if UuidHelper.of().validate(value):
            return Id.__create(value)
        else:
            raise UUIDException('UUID string invalid')

    def equals(self, id: 'Id') -> bool:
        return id.value == self.value
