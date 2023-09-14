from django.urls import include, path

from main_app import views
from main_app import urls
from main_app import query_views

urlpatterns = [
    path("", include(urls)),
    path("", views.home, name="home"),
    path(
        "api/execute_query/<int:query_id>/", views.execute_query, name="execute_query"
    ),
    path(
        "api/download_results/<int:query_id>/",
        views.download_results,
        name="download_results",
    ),
    path('queries/', query_views.query_list, name='query_list'),
    path('queries/<int:query_id>/', query_views.query_detail, name='query_detail'),
    path('queries/new/', query_views.query_create, name='query_create'),
    path('queries/<int:query_id>/edit/', query_views.query_update, name='query_update'),
    path('queries/<int:query_id>/delete/', query_views.query_delete, name='query_delete'),
    path('queries/get_query_from_gpt/', query_views.get_query_from_gpt, name='get_query_from_gpt'),
]
