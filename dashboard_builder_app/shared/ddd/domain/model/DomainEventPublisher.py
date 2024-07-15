# dashboard_builder_app/shared/ddd/domain/model/DomainEventPublisher.py

from typing import Any, List
from .SingletonMeta import SingletonMeta
from .IDomainEvent import IDomainEvent
from .IDomainEventSubscriber import IDomainEventSubscriber

class DomainEventPublisher(metaclass=SingletonMeta):
    __subscribers: List[IDomainEventSubscriber]

    def __init__(self) -> None:
        self.__subscribers = []

    @staticmethod
    def of():
        return DomainEventPublisher()

    def subscribe(self, subscriber: IDomainEventSubscriber):
        self.__subscribers.append(subscriber)

    def unsubscribe(self, id: int):
        self.__subscribers = [s for s in self.__subscribers if id(s) != id]

    def publish(self, event: IDomainEvent) -> Any:
        subscribers = list(filter(lambda subscriber: subscriber.isSubscribedTo(event), self.__subscribers))
        for subscriber in subscribers:
            result = subscriber.handle(event)
            if result:
                return result
