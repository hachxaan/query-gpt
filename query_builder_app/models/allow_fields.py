# query_builder_app/models/allow_fields.py

from django.db import models

from query_builder_app.models.allow_tables import AllowedTable


class AllowedField(models.Model):
    class Meta:
        db_table = 'allowed_field'

    table = models.ForeignKey(AllowedTable, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    description = models.TextField()

    class Meta:
        unique_together = ("table", "name")

    def __str__(self):
        return f"{self.table.name}.{self.name}"
