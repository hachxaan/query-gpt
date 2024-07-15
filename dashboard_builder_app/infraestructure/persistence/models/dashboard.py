# dashboard_builder_app/models/dashboard.py

import json
import uuid
from django.db import models


class DashboardModel(models.Model):
    class Meta:
        db_table = 'dashboard'

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True) 
    description = models.CharField(max_length=255, null=True)
    user_id = models.IntegerField()
    status = models.CharField(max_length=50, null=True, default="pending")
    datatables_columns_config = models.JSONField(null=True)
    highcharts_config = models.JSONField(null=True)
    query = models.TextField(null=True)
    fields = models.TextField(null=True)
    context = models.TextField(null=True)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.description:
            self.description = f"Dashboard {self.id}"
        super(DashboardModel, self).save(*args, **kwargs)

    def get_properties_dict(self):
        properties = {
            'id': self.id,
            'uuid': str(self.uuid),
            'description': self.description,
            'user_id': self.user_id,
            'status': self.status,
            'datatables_columns_config': self.datatables_columns_config,
            'highcharts_config': self.highcharts_config,
            'query': self.query,
            'fields': self.fields,
            'context': self.context,
            'is_public': self.is_public,
            'created_at': self.created_at.strftime('%Y%m%d'),
        }
        print("---------------- DashboardModel ----------------" )
        print(json.dumps(properties, indent=4))
        return properties

    def get_description(self):
        return self.description

    def get_status(self):
        return self.status

    # Métodos get y set para query
    def get_query(self):
        return self.query
    
    def set_query(self, query):
        self.query = query
        self.save()

    # Métodos get y set para datatables_columns_config
    def get_datatables_columns_config(self):
        return self.datatables_columns_config
    
    def set_datatables_columns_config(self, datatables_columns_config):
        self.datatables_columns_config = datatables_columns_config
        self.save()

    # Métodos get y set para highcharts_config
    def get_highcharts_config(self):
        return self.highcharts_config
    
    def set_highcharts_config(self, highcharts_config):
        self.highcharts_config = highcharts_config
        self.save() 

    # Métodos get y set para fields
    def get_fields(self):
        return self.fields
    
    def set_fields(self, fields):
        self.fields = fields
        self.save()

    # Métodos get y set para context
    def get_context(self):
        return self.context
    
    def set_context(self, context):
        self.context = context
        self.save()
