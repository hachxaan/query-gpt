# dashboard_builder_app/infraestructure/web/websocket/routing.py

from django.urls import path
from .consumers import ChatConsumer


websocket_urlpatterns = [
    path('ws/dashboard/<str:dashboard_uuid>/', ChatConsumer.as_asgi()),
]
