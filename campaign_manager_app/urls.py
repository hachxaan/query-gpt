# urls.py

from django.urls import path

from campaign_manager_app import views_mailing_campaign, views_mailing_html
from . import views


urlpatterns = [
    path('mailing_factory/list/', views.mailing_factory_list, name='mailing_factory_list'),
    path('mailing_factory/create/', views.mailing_factory_create, name='mailing_factory_create'),
    path('mailing_factory/update/<int:pk>/', views.mailing_factory_update, name='mailing_factory_update'),
    path('mailing_factory/delete/<int:pk>/', views.mailing_factory_delete, name='mailing_factory_delete'),


    path('campaigns/', views_mailing_campaign.mailing_campaign_list, name='mailing_campaign_list'),
    path('campaigns/create/', views_mailing_campaign.mailing_campaign_create, name='mailing_campaign_create'),
    # path('campaigns/<int:pk>/', views.CampaignDetailView.as_view(), name='campaign_detail'),
    # path('campaigns/<int:pk>/update/', views.CampaignUpdateView.as_view(), name='campaign_update'),
    path('campaigns/<int:pk>/delete/', views_mailing_campaign.mailing_campaign_delete, name='mailing_campaign_delete'),
    
    path('html/<int:pk>/campaigns', views_mailing_html.mailing_html_list_by_campaign, name='mailing_html_list_by_campaign'),
    path('html/<int:pk>/<int:apply_permanent_images>/csv', views_mailing_html.import_csv, name='import_csv'),
    path('html/<int:pk>/delete/', views_mailing_html.delete_mailing_html, name='delete_mailing_html'),
    path('html/download/<int:pk>', views_mailing_html.download_html, name='download_html'),
]
