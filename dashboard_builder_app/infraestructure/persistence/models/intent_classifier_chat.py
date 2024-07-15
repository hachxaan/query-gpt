# dashboard_builder_app/models/main_chat.py


from django.db import models

from dashboard_builder_app.infraestructure.persistence.models.dashboard import DashboardModel


class MainChatModel(models.Model):
    class Meta:
        db_table = 'main_chat'

    id = models.AutoField(primary_key=True)
    dashboard_uuid = models.ForeignKey(DashboardModel, to_field='uuid', on_delete=models.CASCADE)
    chat = models.JSONField()