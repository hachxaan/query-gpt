# backoffice/settings.py

"""
Django settings for backoffice project.

Generated by 'django-admin startproject' using Django 5.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import os
from pathlib import Path
from dotenv import load_dotenv

from backoffice import subcribers_registers
from query_builder_app.ai.openai_validation_query import OpenAIAPIAdapter

ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = ['https://backoffice.multikrd.com']

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


load_dotenv()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-)_ualjle^%!4ifvfx@9hw%v&4#7ufdak-cejkn^@z1d6cs+58o'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap5',
    'channels',
    'backoffice.apps.BackofficeConfig',
    'app',
    "login_app",
    "query_builder_app",
    "campaign_manager_app",
    "dashboard_builder_app",
]

ASGI_APPLICATION = 'backoffice.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],  # Asegúrate de que Redis esté ejecutándose en esta dirección y puerto
        },
    },
}

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'login_app.backends.CustomUserBackend',
]

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/login/"


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'backoffice.middlewares.exception_middleware.ExceptionMiddleware',
    'backoffice.middlewares.user_middleware.UserMiddleware',
]

ROOT_URLCONF = 'backoffice.urls'

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

WSGI_APPLICATION = 'backoffice.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.getenv("NAME_BO"),
        "USER": os.getenv("USER_BO"),
        "PASSWORD": os.getenv("PASSWORD_BO"),
        "HOST": os.getenv("HOST_BO"),
        "PORT": os.getenv("PORT_BO"),
    },
    "query_builder_app_db": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.getenv("NAME_QB"),
        "USER": os.getenv("USER_QB"),
        "PASSWORD": os.getenv("PASSWORD_QB"),
        "HOST": os.getenv("HOST_QB"),
        "PORT": os.getenv("PORT_QB"),
    },
    "campaign_manager_app_db": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.getenv("NAME_CM"),
        "USER": os.getenv("USER_CM"),
        "PASSWORD": os.getenv("PASSWORD_CM"),
        "HOST": os.getenv("HOST_CM"),
        "PORT": os.getenv("PORT_CM"),
    },
    "dashboard_builder_app_db": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.getenv("NAME_DB"),
        "USER": os.getenv("USER_DB"),
        "PASSWORD": os.getenv("PASSWORD_DB"),
        "HOST": os.getenv("HOST_DB"),
        "PORT": os.getenv("PORT_DB"),
    },
    "platform_db": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("POSTGRES_DNS"),
        "PORT": os.getenv("POSTGRES_PORT"),
    },
}


DATABASE_ROUTERS = ['backoffice.db_router.AppRouter']


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/


STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'staticfiles')
]
print(STATIC_ROOT)
# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


openai_adapter = OpenAIAPIAdapter(os.getenv("OPENAI_API_KEY"))

