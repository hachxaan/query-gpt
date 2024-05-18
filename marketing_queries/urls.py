from django.urls import include, path

from main_app import marketing_views, views
from main_app import urls
from file_management import urls as urls_file_management
from html_manager import urls as html_manager_urls
from django.conf.urls import handler404
from main_app import query_views

urlpatterns = [
    path("", include(urls)),
    path("", include(urls_file_management)),
    path("", include(html_manager_urls)),
    path("", views.home, name="home"),
    path("queries", views.query_list_download, name="query_list_download"),
    path(
        "api/execute_query/<int:query_id>/", views.execute_query, name="execute_query"
    ),
    path(
        "api/download_results/<int:query_id>/",
        views.download_results,
        name="download_results",
    ),
    path('queries/manager', query_views.query_list, name='query_list'),
    path('queries/<int:query_id>/', query_views.query_detail, name='query_detail'),
    path('queries/new/', query_views.query_create, name='query_create'),
    path('queries/<int:query_id>/edit/', query_views.query_update, name='query_update'),
    path('queries/<int:query_id>/delete/', query_views.query_delete, name='query_delete'),
    path('queries/get_query_from_gpt/', query_views.get_query_from_gpt, name='get_query_from_gpt'),
    path('table/chat/config_report/', query_views.config_report, name='config_report'),


    path('data/', query_views.fetch_data, name='fetch_data'),
    path('table/', query_views.table, name='table'),
    path('chart/', query_views.chart, name='chart'),
    path('chat_database/', query_views.chat_database, name='chat_database'),
    # path('marketing/files', marketing_views.marketing_files , name='marketing_files'),

]

handler404 = 'main_app.views.error_404' 
