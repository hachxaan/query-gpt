from django.db import models

# Create your models here.



class MailingCampaign(models.Model):
    id = models.AutoField(primary_key=True)
    # template = models.ForeignKey(MailingTemplate, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    apply_permanent_images = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name
    
class MailingHTML(models.Model):
    id = models.AutoField(primary_key=True)
    mailing_campaign = models.ForeignKey(MailingCampaign, on_delete=models.CASCADE)
    white_label = models.CharField(max_length=255)
    csv_data = models.TextField()
    html_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.white_label + ' - ' + self.mailing_campaign.name
    

