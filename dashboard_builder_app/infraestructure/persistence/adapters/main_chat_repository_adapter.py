# dashboard_builder_app/infraestructure/persistence/adapters/main_chat_repository_adapter.py


from typing import List, Dict
from dashboard_builder_app.domain.repositories.main_chat_repository import IMainChat
from dashboard_builder_app.infraestructure.persistence.services.chat_proxy_orm_service import ChatProxyORMService
from dashboard_builder_app.shared.ddd.domain.model.Id import Id

class MainChatRespositoryAdapter(IMainChat):

    def __init__(self, chat_proxy_orm_service: ChatProxyORMService):
        self.chat_proxy_service = chat_proxy_orm_service

    def get_chat_history(self, dashboard_uuid: Id) -> List:
        print("Id of dashboard_uuid: ", dashboard_uuid)
        return self.chat_proxy_service.get_chat_history(dashboard_uuid=dashboard_uuid)

    def add_formatted_message_to_chat(self, dashboard_uuid: Id, message_json: Dict):
        return self.chat_proxy_service.add_formatted_message_to_chat(dashboard_uuid, message_json)

    def get_chat(self, chat_id: int) -> List:
        return self.chat_proxy_service.get_chat(chat_id)

    def set_chat(self, chat_id: int, chat: List):
        return self.chat_proxy_service.set_chat(chat_id, chat)

    def add_message_to_chat(self, chat_id: int, message: Dict):
        return self.chat_proxy_service.add_message_to_chat(chat_id, message)

    def get_last_message_from_chat(self, chat_id: int) -> Dict:
        return self.chat_proxy_service.get_last_message_from_chat(chat_id)

    def get_or_create_by_id(self, chat_id: int, **kwargs) -> Dict:
        return self.chat_proxy_service.get_or_create_by_id(chat_id, **kwargs)
