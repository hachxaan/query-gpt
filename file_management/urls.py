# urls.py

from django.urls import path
from . import views


urlpatterns = [
    path('mailing_factory/list/', views.mailing_factory_list, name='mailing_factory_list'),
    path('mailing_factory/create/', views.mailing_factory_create, name='mailing_factory_create'),
    path('mailing_factory/update/<int:pk>/', views.mailing_factory_update, name='mailing_factory_update'),
    path('mailing_factory/delete/<int:pk>/', views.mailing_factory_delete, name='mailing_factory_delete'),
]
