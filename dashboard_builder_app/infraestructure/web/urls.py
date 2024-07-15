# dashboard_builder_app/infraestructure/web/urls.py


from django.urls import path
from dashboard_builder_app.infraestructure.web.endpoints.home import home
from dashboard_builder_app.infraestructure.web.endpoints.dashboard_builder_view import dashboard_builder_view
from dashboard_builder_app.infraestructure.web.endpoints.dashboard_create_view import dashboard_create_view
from dashboard_builder_app.infraestructure.web.endpoints.dashboard_chat_view import dashboard_chat_view

app_name = 'dashboard_builder_app'


urlpatterns = [
    path("dashboard/", home, name="home"),
    path('dashboard/<str:uuid>/builder/', dashboard_builder_view, name='dashboard_builder'),
    path('dashboard/create/', dashboard_create_view, name='dashboard_create'),
    path('dashboard/<str:uuid>/builder/chat/', dashboard_chat_view, name='dashboard_chat'),
]
