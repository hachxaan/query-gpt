# dashboard_builder_app/models/sql_chat.py


from dashboard_builder_app.infraestructure.persistence.models.dashboard import DashboardModel
from sqlalchemy import Column, Text
from django.db import models



class SQLChatModel(models.Model):
    class Meta:
        db_table = 'sql_chat'
    
    id = models.AutoField(primary_key=True)
    dashboard_uuid = models.ForeignKey(DashboardModel, to_field='uuid', on_delete=models.CASCADE)
    chat_context = models.TextField(null=True)
