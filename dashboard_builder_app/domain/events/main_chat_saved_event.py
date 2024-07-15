
# dashboard_builder_app/domain/events/main_chat_saved_event.py


from dashboard_builder_app.domain.entities.classifier_entity import ClassifierEntity
from dashboard_builder_app.shared.ddd.domain.model.DateA import DateA
from dashboard_builder_app.shared.ddd.domain.model.IDomainEvent import IDomainEvent



class MainChatSavedEvent(IDomainEvent):
    """ ev- """

    __occurredOn: DateA
    __classifier: ClassifierEntity

    def __init__(self, classifier: ClassifierEntity) -> None:
        self.__occurredOn = DateA.create()
        self.__classifier = classifier

    def getClassifier(cls) -> ClassifierEntity:
        return cls.__classifier

    @classmethod
    def getOccurredOn(cls) -> DateA:
        return cls.__occurredOn
