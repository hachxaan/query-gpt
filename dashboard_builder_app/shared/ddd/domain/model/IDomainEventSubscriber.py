from abc import ABCMeta, abstractmethod

from .IDomainEvent import IDomainEvent


class IDomainEventSubscriber(metaclass=ABCMeta):

    @abstractmethod
    def handle(event: IDomainEvent):
        pass

    @abstractmethod
    def isSubscribedTo(event: IDomainEvent) -> bool:
        pass
