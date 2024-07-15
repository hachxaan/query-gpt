# dashboard_builder_app/infraestructure/persistence/models/agents.py

import uuid
from django.db import models


class AiAgentModel(models.Model):
    class Meta:
        db_table = 'ai_agent'


    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, null=False)
    description = models.CharField(max_length=255, null=True)
    model = models.CharField(max_length=32, null=True)
    prompt_template = models.TextField(null=True)
    temperature = models.FloatField(null=True, default=0.0)
    max_tokens = models.IntegerField(null=True, default=150)

