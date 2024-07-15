# query_builder_app/models/allow_tables.py

from django.db import models

class AllowedTable(models.Model):
    class Meta:
        db_table = 'allowed_table'

    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name