# dashboard_builder_app/application/subscibers/dashboard_created_subscriber.py


from dashboard_builder_app.domain.events.dashboard_created_event import MainChatSavedEvent
from dashboard_builder_app.domain.repositories.dashboard_repository import IDashboard
from dashboard_builder_app.shared.ddd.domain.model.IDomainEvent import IDomainEvent
from dashboard_builder_app.shared.ddd.domain.model.IDomainEventSubscriber import IDomainEventSubscriber



class DashboardCreatedSubscriber(IDomainEventSubscriber):

    def __init__(self, dashboard_repository: IDashboard):
        self.dashboard_repository = dashboard_repository

    def handle(self, event: MainChatSavedEvent):
        dashboard = event.getDashboard()
        return self.dashboard_repository.save_dashboard(dashboard)

    def isSubscribedTo(self, event: IDomainEvent) -> bool:
        return isinstance(event, MainChatSavedEvent)
