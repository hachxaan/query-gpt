"""
Django settings for marketing_queries project.

Generated by 'django-admin startproject' using Django 4.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import os

from dotenv import load_dotenv
from main_app.utils.adapters.openai_configure_table import OpenAIAPITableAdapter
from main_app.utils.adapters.openai_create_query import OpenAIAPIQueryAdapter
from main_app.utils.adapters.openai_get_context import OpenAIAPIGetContextAdapter

from main_app.utils.adapters.openai_validation_query import (
    OpenAIAPIAdapter,
)

# from sshtunnel import SSHTunnelForwarder

# import socks
# import socket
# socks.set_default_proxy(socks.SOCKS5, "localhost", 8080)
# socket.socket = socks.socksocket

load_dotenv()

# print((os.getenv("SSH_TUNNEL_HOST"), int(os.getenv("SSH_TUNNEL_PORT"))))

# def create_db_tunnel():
#     server = SSHTunnelForwarder(
#         (os.getenv("SSH_TUNNEL_HOST"), int(os.getenv("SSH_TUNNEL_PORT"))),
#         ssh_username=os.getenv("SSH_TUNNEL_USER"),
#         ssh_password=os.getenv("SSH_TUNNEL_PASSWORD"),
#         remote_bind_address=(os.getenv("POSTGRES_DNS"), int(os.getenv("POSTGRES_PORT")))
#     )

#     server.start()

#     return {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": os.getenv("POSTGRES_DB"),
#         "USER": os.getenv("POSTGRES_USER"),
#         "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
#         "HOST": "127.0.0.1",  # localhost porque estamos haciendo un túnel a la base de datos
#         "PORT"s: server.local_bind_port,  # El puerto local asignado al túnel
#     }


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-bw-!=24$v_yl(z=bruc761o_k1z%7652hnynh!&*shspr54ud_"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = ['https://backoffice.multikrd.com']

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'crispy_forms',
    'crispy_bootstrap5',
    "main_app",
    "login_app",
    "file_management",
    "html_manager",
]



AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'main_app.backends.CustomUserBackend',
]

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/login/"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    'main_app.middleware.ExceptionMiddleware',
]

ROOT_URLCONF = "marketing_queries.urls"


CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "marketing_queries.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.getenv("POSTGRES_DB_MKT"),
        "USER": os.getenv("POSTGRES_USER_MKT"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD_MKT"),
        "HOST": os.getenv("POSTGRES_DNS_MKT"),
        "PORT": os.getenv("POSTGRES_PORT_MKT"),
    },
    "platform_db": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("POSTGRES_DNS"),
        "PORT": os.getenv("POSTGRES_PORT"),
    },
    # "platform_db": create_db_tunnel(),
}

openai_adapter = OpenAIAPIAdapter(os.getenv("OPENAI_API_KEY"))
openai_adapter_get_query = OpenAIAPIQueryAdapter(os.getenv("OPENAI_API_KEY"))
openai_adapter_configure_table = OpenAIAPITableAdapter(os.getenv("OPENAI_API_KEY"))
openai_adapter_get_context = OpenAIAPIGetContextAdapter(os.getenv("OPENAI_API_KEY"))

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

# TIME_ZONE = "America/Mexico_City"
TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

#   STATIC_URL = "static/"
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
