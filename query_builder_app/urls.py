# query_builder_app/urls.py

from django.urls import path

from query_builder_app.views.mailing_audiencias.views import GenerateAndDownloadCSVAudiencesView
from query_builder_app.views.query_list import query_list, query_create, query_update, query_delete, get_query_from_gpt
from query_builder_app.views.query_list_download import query_list_download
from django.views.generic import TemplateView

urlpatterns = [

    path("queries", query_list_download, name="query_list_download"),
    path('queries/manager', query_list, name='query_list'),
    path('queries/new/', query_create, name='query_create'),

    path('queries/<int:query_id>/edit/', query_update, name='query_update'),
    path('queries/<int:query_id>/delete/', query_delete, name='query_delete'),
    path('queries/get_query_from_gpt/', get_query_from_gpt, name='get_query_from_gpt'),

    path('generate-csv-audiences/', GenerateAndDownloadCSVAudiencesView.as_view(), name='generate_csv_audiences'),
    path('audiences/', TemplateView.as_view(template_name='queries/audiences.html'), name='audiences'),
]



