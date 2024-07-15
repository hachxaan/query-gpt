# dashboard_builder_app/application/subscibers/dashboard_created_subscriber.py


from dashboard_builder_app.domain.events.main_chat_saved_event import MainChatSavedEvent
from dashboard_builder_app.domain.repositories.main_chat_repository import IMainChat
from dashboard_builder_app.shared.ddd.domain.model.IDomainEvent import IDomainEvent
from dashboard_builder_app.shared.ddd.domain.model.IDomainEventSubscriber import IDomainEventSubscriber



class MainChatSavedSubscriber(IDomainEventSubscriber):

    def __init__(self, main_chat_repository: IMainChat):
        self.main_chat_repository = main_chat_repository

    def handle(self, event: MainChatSavedEvent):
        classifier = event.getClassifier()


        return self.main_chat_repository.add_formatted_message_to_chat(dashboard)

    def isSubscribedTo(self, event: IDomainEvent) -> bool:
        return isinstance(event, MainChatSavedEvent)
