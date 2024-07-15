# campaign_manager_app/models/mailing_html.py

from django.db import models
from campaign_manager_app.models.mailing_campaign import MailingCampaign


class MailingHTML(models.Model):

    class Meta:
        db_table = 'mailing_html'

    id = models.AutoField(primary_key=True)
    mailing_campaign = models.ForeignKey(MailingCampaign, on_delete=models.CASCADE)
    white_label = models.CharField(max_length=255)
    csv_data = models.TextField()
    html_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.white_label + ' - ' + self.mailing_campaign.name