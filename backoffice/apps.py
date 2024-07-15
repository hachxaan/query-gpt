# backoffice/apps.py

from django.apps import AppConfig

class BackofficeConfig(AppConfig):
    name = 'backoffice'

    def ready(self):
        from . import subcribers_registers
        subcribers_registers.register_subscribers()
