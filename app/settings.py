#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Django settings for prototype project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '@0jnn4oh3h2ri-y6skgfea!&07o+5z8#oamzh-1nmm)wq*p(e%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Core
    'core',
    'transcribe',
    'order',
    'django_rq',

    # API
    'rest_framework',
    'api',

    # Web
    'frontend',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'app.urls'

WSGI_APPLICATION = 'app.wsgi.application'


#
# Auth
#

AUTHENTICATION_BACKENDS = (
    'core.auth_backends.EmailAuthBackend',
)


#
# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'transcribe',
        'USER': 'transcribe',
        'PASSWORD': 'transcribe',
        'HOST': 'db.transcribe.ninja',
        'OPTIONS': {
            'init_command': 'SET storage_engine=INNODB,character_set_connection=utf8,collation_connection=utf8_unicode_ci'
        }
    }
}

# Redis queue for async jobs
RQ_QUEUES = {
    # Staff
    'prepare': {
        'HOST': 'db.transcribe.ninja',
        'PORT': 6379,
        'DB': 0,
        'PASSWORD': '',
        'DEFAULT_TIMEOUT': 360,
    },
    # Analys audio
    'diarization': {
        'HOST': 'db.transcribe.ninja',
        'PORT': 6379,
        'DB': 1,
        'PASSWORD': '',
        'DEFAULT_TIMEOUT': 360,
    },
    # Split audio
    'queue': {
        'HOST': 'db.transcribe.ninja',
        'PORT': 6379,
        'DB': 2,
        'PASSWORD': '',
        'DEFAULT_TIMEOUT': 360,
    }
}

# Fixtures
FIXTURE_DIRS = (
    os.path.join(BASE_DIR, "app/fixtures/"),
)

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

DEFAULT_CHARSET = 'utf8'


#
# API
#

# Rest Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny'
    ],
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler'
}


#
# Files
#


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, "static/")

if DEBUG:
    FRONTEND_ROOT = os.path.join(BASE_DIR, "frontend/build/")
    STATICFILES_DIRS = (
        FRONTEND_ROOT,
        os.path.join(BASE_DIR, "frontend/bin/"),
    )

STATIC_URL = '/static/'

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

# S3 Config
AWS_ACCESS_KEY_ID = 'AKIAJT4XGM5CW5RT2EHQ'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'transcribe-ninja'

# Media content
MEDIA_ROOT = os.path.join(BASE_DIR, "media/")

# Records content
RECORD_ROOT = os.path.join(MEDIA_ROOT, "record/")
PIECE_ROOT = os.path.join(MEDIA_ROOT, "piece/")

TEMP_DIR = os.path.join(BASE_DIR, "temp/")



#
# Record
#

# Подсчёт скорости разговора
# Средняя скорость произношения. Знаков в секунду
SPEECH_SPEED = 22
# Сколько минимум записи должно быть распознано, 
# чтобы посчтитать скорость произоншения
SPEECH_SPEED_MIN_DURATION = 120 

# Diarization
VOICEID_DB_PATH = 'transcribe/voiceid'

