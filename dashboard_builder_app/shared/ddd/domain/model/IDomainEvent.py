from abc import ABCMeta, abstractmethod

from .DateA import DateA


class IDomainEvent(metaclass=ABCMeta):

    @abstractmethod
    def getOccurredOn() -> DateA:
        pass
