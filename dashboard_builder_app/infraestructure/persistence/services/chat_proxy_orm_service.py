# dashboard_builder_app/infraestructure/persistence/services/chat_proxy_orm_service.py

from typing import Dict, List
from dashboard_builder_app.infraestructure.exception.dashboard_not_found_exception import DashboardNotFoundException
from dashboard_builder_app.infraestructure.persistence.models.intent_classifier_chat import MainChatModel
from dashboard_builder_app.infraestructure.persistence.models.dashboard import DashboardModel
from dashboard_builder_app.shared.ddd.domain.model.Id import Id
from django.core.exceptions import ObjectDoesNotExist
from channels.db import database_sync_to_async

class ChatProxyORMService:

    def get_chat_history(self, dashboard_uuid: Id) -> List:
        try:
            main_chat = MainChatModel.objects.get(dashboard_uuid__uuid=dashboard_uuid.value)
            return main_chat.chat
        except ObjectDoesNotExist:
            return []
        except Exception as e:
            msg = f"Error: {str(e)}"
            print(msg)
            raise Exception(msg)
        
    # @database_sync_to_async
    def add_formatted_message_to_chat(self, dashboard_uuid: Id, message_json: Dict):
        try:
            dashboard = DashboardModel.objects.get(uuid=dashboard_uuid.value)
            main_chat, _ = MainChatModel.objects.get_or_create(dashboard_uuid=dashboard, defaults={"chat": []} )
        except DashboardModel.DoesNotExist:
            raise DashboardNotFoundException(f"Dashboard with UUID {dashboard_uuid.value} not found.")
        
        formatted_message = {
            "sender": message_json.get("sender", ""),
            "text": message_json.get("text", "")
        }
        
        if message_json.get("request_type") in ["1", "2"] and "query" in message_json:
            formatted_message["text"] = f"{message_json.get('text', '')}\nEsta es la consulta:\n<code>{message_json['query']}</code>"
        
        self.add_message_to_chat(main_chat, formatted_message)
        return formatted_message

    def get_chat(self, chat_id: int) -> List:
        try:
            main_chat = MainChatModel.objects.get(id=chat_id)
            return main_chat.chat
        except MainChatModel.DoesNotExist:
            raise DashboardNotFoundException(f"Chat with id {chat_id} not found.")
    
    def set_chat(self, chat_id: int, chat: List):
        try:
            main_chat = MainChatModel.objects.get(id=chat_id)
            main_chat.chat = chat
            main_chat.save()
        except MainChatModel.DoesNotExist:
            raise DashboardNotFoundException(f"Chat with id {chat_id} not found.")
    
    def add_message_to_chat(self, main_chat: MainChatModel, message: Dict):
        if main_chat.chat is None:
            main_chat.chat = []
        main_chat.chat.append(message)
        main_chat.save()
    
    def get_last_message_from_chat(self, chat_id: int) -> Dict:
        try:
            main_chat = MainChatModel.objects.get(id=chat_id)
            return main_chat.chat[-1] if main_chat.chat else None
        except MainChatModel.DoesNotExist:
            raise DashboardNotFoundException(f"Chat with id {chat_id} not found.")
    
    def get_or_create_by_id(self, chat_id: int, **kwargs) -> MainChatModel:
        try:
            instance = MainChatModel.objects.get(id=chat_id)
        except MainChatModel.DoesNotExist:
            instance = MainChatModel.objects.create(id=chat_id)
            instance.save()
            self.add_formatted_message_to_chat(instance.id, kwargs)
        return instance
