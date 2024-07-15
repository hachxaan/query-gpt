# campaign_manager_app/models/mailing_campaign.py


from django.db import models


class MailingCampaign(models.Model):
    class Meta:
        db_table = 'mailing_campaign'

    id = models.AutoField(primary_key=True)
    # template = models.ForeignKey(MailingTemplate, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    apply_permanent_images = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name