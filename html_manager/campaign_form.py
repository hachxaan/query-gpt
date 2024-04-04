from django import forms
from .models import MailingCampaign




class MailingCampaignForm(forms.ModelForm):
    class Meta:
        model = MailingCampaign
        fields = ['name', 'description', 'apply_permanent_images']