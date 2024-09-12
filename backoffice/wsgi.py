# backoffice/wsgi.py

"""
WSGI config for backoffice project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os
from query_builder_app.views.banking.card_report_service import cleanup_temp_files
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backoffice.settings')

application = get_wsgi_application()

def application_with_cleanup(environ, start_response):
    """WSGI application wrapper that performs cleanup after the response is sent."""
    def custom_start_response(status, headers, exc_info=None):
        environ['wsgi.file_wrapper'] = None  # Disable file wrapper to prevent premature file closure
        return start_response(status, headers, exc_info)

    response_iter = application(environ, custom_start_response)
    
    def cleanup_wrapper():
        yield from response_iter
        # Perform cleanup after the response has been fully sent
        temp_dir = environ.get('temp_dir')
        if temp_dir:
            cleanup_temp_files(temp_dir)

    return cleanup_wrapper()