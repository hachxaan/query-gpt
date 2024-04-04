import os
from django.db import models

class MailingFactory(models.Model):
    id = models.AutoField(primary_key=True)
    white_label = models.CharField(max_length=255)
    name = models.CharField(max_length=255, unique=True) 
    type = models.CharField(max_length=255)
    campaign = models.CharField(max_length=255)
    permanent = models.BooleanField(default=False)
    file_name = models.CharField(max_length=255)
    href = models.TextField(default='')
    extension = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    @property
    def file_url(self):
        # Assuming the file is stored in a specific directory
        host = os.environ.get('HOST_ASSETS', 'platform.multikrd.com')
        path = os.environ.get('PATH_ASSETS', '/mailing/statics/')
        url = f"https://{host}{path}{self.white_label}-{self.file_name}{self.extension}"
        return url
    
    def __str__(self):
        return self.name


# class MailingTemplate(models.Model):
#     id = models.AutoField(primary_key=True)
#     name = models.CharField(max_length=255)
#     html = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     def __str__(self):
#         return self.name
