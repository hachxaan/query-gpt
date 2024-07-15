# dashboard_builder_app/domain/events/dashboard_created_event.py


from dashboard_builder_app.domain.entities.dashboard_entity import DashboardEntity
from dashboard_builder_app.shared.ddd.domain.model.DateA import DateA
from dashboard_builder_app.shared.ddd.domain.model.IDomainEvent import IDomainEvent



class MainChatSavedEvent(IDomainEvent):
    """ ev- """

    __occurredOn: DateA
    __dashboard: DashboardEntity

    def __init__(self, dashboard: DashboardEntity) -> None:
        self.__occurredOn = DateA.create()
        self.__dashboard = dashboard

    def getDashboard(cls) -> DashboardEntity:
        return cls.__dashboard

    @classmethod
    def getOccurredOn(cls) -> DateA:
        return cls.__occurredOn
