export DJANGO_SETTINGS_MODULE=backoffice.settings

gunicorn -c gunicorn_config.py backoffice.asgi:application
