from django.urls import include, path

from main_app import marketing_views, views
from main_app import urls
from file_management import urls as urls_file_management
from html_manager import urls as html_manager_urls
from main_app import query_views

ROOT_PATH = 'backoffice'

urlpatterns = [
    path(ROOT_PATH + "/", include(urls)),
    path(ROOT_PATH + "/", include(urls_file_management)),
    path(ROOT_PATH + "/", include(html_manager_urls)),
    path(ROOT_PATH + "/", views.home, name="home"),
    path(ROOT_PATH + "/queries", views.query_list_download, name="query_list_download"),
    path(
        ROOT_PATH + "/api/execute_query/<int:query_id>/", views.execute_query, name="execute_query"
    ),
    path(
        ROOT_PATH + "/api/download_results/<int:query_id>/",
        views.download_results,
        name="download_results",
    ),
    path(ROOT_PATH + "/queries/manager", query_views.query_list, name="query_list"),
    path(ROOT_PATH + "/queries/<int:query_id>/", query_views.query_detail, name="query_detail"),
    path(ROOT_PATH + "/queries/new/", query_views.query_create, name="query_create"),
    path(ROOT_PATH + "/queries/<int:query_id>/edit/", query_views.query_update, name="query_update"),
    path(ROOT_PATH + "/queries/<int:query_id>/delete/", query_views.query_delete, name="query_delete"),
    path(ROOT_PATH + "/queries/get_query_from_gpt/", query_views.get_query_from_gpt, name="get_query_from_gpt"),
    path(ROOT_PATH + "/table/chat/config_report/", query_views.config_report, name="config_report"),
    path(ROOT_PATH + "/data/", query_views.fetch_data, name="fetch_data"),
    path(ROOT_PATH + "/table/", query_views.table, name="table"),
    path(ROOT_PATH + "/chart/", query_views.chart, name="chart"),
    path(ROOT_PATH + "/chat_database/", query_views.chat_database, name="chat_database"),
    # path(ROOT_PATH + "/marketing/files", marketing_views.marketing_files , name="marketing_files"),
]

