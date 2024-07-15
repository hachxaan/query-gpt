# dashboard_builder_app/infraestructure/web/websocket/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from dashboard_builder_app.infraestructure.persistence.services.chat_proxy_orm_service import ChatProxyORMService
from dashboard_builder_app.shared.ddd.domain.model.Id import Id

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.dashboard_uuid = self.scope['url_route']['kwargs']['dashboard_uuid']
        self.room_group_name = f'chat_{self.dashboard_uuid}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Usar database_sync_to_async para operaciones de base de datos
        await self.add_message_to_chat(Id.ofString(self.dashboard_uuid), message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def chat_message(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))

    @database_sync_to_async
    def add_message_to_chat(self, dashboard_uuid, message):
        print(f"Adding message to chat {dashboard_uuid}")
        chat_service = ChatProxyORMService()
        chat_service.add_formatted_message_to_chat(dashboard_uuid, message)
