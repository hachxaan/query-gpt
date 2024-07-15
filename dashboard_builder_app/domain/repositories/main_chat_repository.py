# dashboard_builder_app/domain/repositories/main_chat_repository.py


from abc import ABC, abstractmethod
from typing import List, Dict
from dashboard_builder_app.shared.ddd.domain.model.Id import Id

class IMainChat(ABC):

    @abstractmethod
    def get_chat_history(self, dashboard_uuid: Id) -> List:
        pass

    @abstractmethod
    def add_formatted_message_to_chat(self, dashboard_uuid: Id, message_json: Dict):
        pass

    @abstractmethod
    def get_chat(self, chat_id: int) -> List:
        pass

    @abstractmethod
    def set_chat(self, chat_id: int, chat: List):
        pass

    @abstractmethod
    def add_message_to_chat(self, chat_id: int, message: Dict):
        pass

    @abstractmethod
    def get_last_message_from_chat(self, chat_id: int) -> Dict:
        pass

    @abstractmethod
    def get_or_create_by_id(self, chat_id: int, **kwargs) -> Dict:
        pass
