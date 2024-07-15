from datetime import datetime
import re

from .Pattern import Pattern
from .SingletonMeta import SingletonMeta


class DateHelper(metaclass=SingletonMeta):

    @staticmethod
    def of() -> 'DateHelper':
        return DateHelper()

    def generate(self) -> datetime:
        return datetime.utcnow()

    def validate(self, value: str) -> bool:
        if not (re.compile(Pattern.Date_ISO8601.value).search(value)):
            raise ValueError(
                f'Invalid date: {value}, require format: ISO8601'
            )
        return True
