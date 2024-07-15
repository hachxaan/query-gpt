# backoffice/urls.py

from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views
from app import views_app
from login_app.views import ChangePasswordView, LoginFromView
from query_builder_app import urls as query_builder_urls
from campaign_manager_app import urls as campaign_manager_urls
from dashboard_builder_app.infraestructure.web import urls as dashboard_builder_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path("login/", LoginFromView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path("", views_app.home, name="home"),


    # QUIERY BUILDER
    path("", include(query_builder_urls)),

    # Campaign Manager
    path("", include(campaign_manager_urls)),

    # Dashboard Builder
    path("", include(dashboard_builder_urls)),


]


