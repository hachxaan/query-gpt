# src\shared\ddd\domain\model\EntityRoot.py

from abc import abstractmethod
from typing import Any
from .DomainEventPublisher import DomainEventPublisher

from .IDomainEvent import IDomainEvent


class EntityRoot():

    @abstractmethod
    def publishEvent(event: IDomainEvent) -> Any:
        return DomainEventPublisher.of().publish(event)
