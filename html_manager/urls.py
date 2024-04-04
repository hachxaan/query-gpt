from django.urls import path
from . import views_mailing_campaign
from . import views_mailing_html


urlpatterns = [
    path('campaigns/', views_mailing_campaign.mailing_campaign_list, name='mailing_campaign_list'),
    path('campaigns/create/', views_mailing_campaign.mailing_campaign_create, name='mailing_campaign_create'),
    # path('campaigns/<int:pk>/', views.CampaignDetailView.as_view(), name='campaign_detail'),
    # path('campaigns/<int:pk>/update/', views.CampaignUpdateView.as_view(), name='campaign_update'),
    path('campaigns/<int:pk>/delete/', views_mailing_campaign.mailing_campaign_delete, name='mailing_campaign_delete'),
    
    path('html/<int:pk>/campaigns', views_mailing_html.mailing_html_list_by_campaign, name='mailing_html_list_by_campaign'),
    path('html/<int:pk>/csv', views_mailing_html.import_csv, name='import_csv'),
    path('html/<int:pk>/delete/', views_mailing_html.delete_mailing_html, name='delete_mailing_html'),
    path('html/download/<int:pk>', views_mailing_html.download_html, name='download_html'),
]