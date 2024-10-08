# campaign_manager_app/forms.py

from django import forms
from .models import MailingCampaign, MailingFactory


type_choices = [
    ('header', 'header'),
    ('body', 'body'),
    ('footer', 'footer')
]

class FileUploadForm(forms.ModelForm):
    type = forms.ChoiceField(choices=type_choices)
    file = forms.FileField()
    href = forms.URLField(required=False)  # Hace que el campo no sea obligatorio

    class Meta:
        model = MailingFactory
        fields = ['white_label', 'permanent', 'name', 'type', 'href', 'campaign']
        exclude = ['create_at', 'file_name']

    def __init__(self, *args, **kwargs):
        super(FileUploadForm, self).__init__(*args, **kwargs)
        self.fields['href'].required = False 



class MailingCampaignForm(forms.ModelForm):
    class Meta:
        model = MailingCampaign
        fields = ['name', 'description', 'apply_permanent_images']