import uuid
from .SingletonMeta import SingletonMeta


class UuidHelper(metaclass=SingletonMeta):

    @staticmethod
    def of() -> 'UuidHelper':
        return UuidHelper()

    def generate(self) -> str:
        return uuid.uuid4()

    def validate(self, value: str) -> bool:
        try:
            uuid_obj = uuid.UUID(value, version=4)
        except ValueError:
            return False
        return (str(uuid_obj) == value)
