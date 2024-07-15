# gunicorn_config.py

import multiprocessing
import os

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"

os.environ['DJANGO_SETTINGS_MODULE'] = 'backoffice.settings'
