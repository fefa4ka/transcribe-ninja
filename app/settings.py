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
from hosts import HOSTS

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

PROJECT_NAME = 'transcribe-ninja'
DOMAIN = 'transcribe.ninja'

EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_HOST_USER = DEFAULT_FROM_EMAIL = 'info@transcribe.ninja'
EMAIL_HOST_PASSWORD = 'cntyjuhfa,kznm'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# 
# HOSTS = {
#     'DB': 'db.%s' % DOMAIN,
#     'ENGINE': 'engine.%s' % DOMAIN,
#     'WEB': DOMAIN
# }

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '@0jnn4oh3h2ri-y6skgfea!&07o+5z8#oamzh-1nmm)wq*p(e%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

PROJECT_DIR = '~/' + PROJECT_NAME
ENV_DIR = '%s/env' % PROJECT_DIR
LOGS_DIR = '~/logs'
ACTIVATE = '. %s/bin/activate' % ENV_DIR

REPOSITORY = 'git@github.com:fefa4ka/%s.git' % PROJECT_NAME
GIT_USERNAME = 'fefa4ka'
ADMIN_EMAIL = 'fefa4ka@gmail.com'
GIT_KEY_PATH = '/Users/fefa4ka/.ssh/deploy_rsa'
GIT_KEY_NAME = 'github_rsa'

YANDEX_API_KEY = 'aa0f1865-e414-42d2-9c50-cff9a64743a0'
UUID = '12345A781234567B1234567812345678'


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
    'work',
    'django_rq',

    # API
    'rest_framework',
    'rest_framework.authtoken',
    'api',
    'djoser',

    # Web
    'frontend',
    'social_auth'
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
#
#
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    # 'django.core.context_processors.request',
    'social_auth.context_processors.social_auth_by_name_backends',
)


#
# Auth
#
DJOSER = {
    'DOMAIN': DOMAIN,
    'SITE_NAME': 'Transcribe.ninja',
    'PASSWORD_RESET_CONFIRM_URL': '#/password/reset/confirm/{uid}/{token}',
    'ACTIVATION_URL': '#/activate/{uid}/{token}',
    'LOGIN_AFTER_ACTIVATION': True,
    'SEND_ACTIVATION_EMAIL': True,
}

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

AUTHENTICATION_BACKENDS = (
    'core.auth_backends.EmailAuthBackend',
    'social_auth.backends.facebook.FacebookBackend',
    'social_auth.backends.google.GoogleOAuth2Backend',
    'social_auth.backends.contrib.vk.VKOAuth2Backend',
    'django.contrib.auth.backends.ModelBackend',
)

# Разрешаем создавать пользователей через social_auth
SOCIAL_AUTH_CREATE_USERS = True
SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL = True
SOCIAL_AUTH_SLUGIFY_USERNAMES = False

# Перечислим pipeline, которые последовательно буду обрабатывать респонс
SOCIAL_AUTH_PIPELINE = (
    # Получает по backend и uid инстансы social_user и user
    'social_auth.backends.pipeline.social.social_auth_user',
    # Получает по user.email инстанс пользователя и заменяет собой тот, который получили выше.
    # Кстати, email выдает только Facebook и GitHub, а Vkontakte и Twitter не выдают
    'social_auth.backends.pipeline.associate.associate_by_email',
    # Пытается собрать правильный username, на основе уже имеющихся данных
    'social_auth.backends.pipeline.user.get_username',
    # Создает нового пользователя, если такого еще нет
    'social_auth.backends.pipeline.user.create_user',
    # Пытается связать аккаунты
    'social_auth.backends.pipeline.social.associate_user',
    # Получает и обновляет social_user.extra_data
    'social_auth.backends.pipeline.social.load_extra_data',
    # Обновляет инстанс user дополнительными данными с бекенда
    'social_auth.backends.pipeline.user.update_user_details'
)

SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/'

# Google Oauth2
GOOGLE_API_KEY = 'AIzaSyC6CGz9s-XTNsIZd5JaowVG0oU8dJvTkTg'
GOOGLE_OAUTH2_CLIENT_ID = '923396664540-1ok2s8c2q8v23c7jpffkjv74m2a5n431.apps.googleusercontent.com'
GOOGLE_OAUTH2_CLIENT_SECRET = 'vuDE6XLSEhZS_mC-ScqnXr5V'

# Facebook API
FACEBOOK_APP_ID              = '981908478505313'
FACEBOOK_API_SECRET          = '381bb9a5253a2addf5afd818a7a17209'
FACEBOOK_EXTENDED_PERMISSIONS = ['email']

# VK Api
VK_APP_ID = '4754043'
VK_API_SECRET = 'fLri3IgiQBCRidQ782bM'
# VK_EXTRA_SCOPE = ['email']


#
# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'transcribe',
        'USER': 'transcribe',
        'PASSWORD': 'transcribe',
        'HOST': HOSTS['DB'],
        'OPTIONS': {
            'init_command': 'SET storage_engine=INNODB,character_set_connection=utf8,collation_connection=utf8_unicode_ci'
        }
    }
}

# AWS RDS Config
RDS_ALLOCATED_STORAGE = '5'
RDS_INSTANCE_CLASS = 'db.t2.micro'
RDS_ENGINE = 'MySQL'


# Redis queue for async jobs
RQ_QUEUES = {
    # Staff
    'prepare': {
        'HOST': HOSTS['REDIS'],
        'PORT': 6379,
        'DB': 0,
        'PASSWORD': '',
        'DEFAULT_TIMEOUT': 360,
    },
    # Analys audio
    'analys': {
        'HOST': HOSTS['REDIS'],
        'PORT': 6379,
        'DB': 1,
        'PASSWORD': '',
        'DEFAULT_TIMEOUT': 360,
    },
    # Split audio
    'queue': {
        'HOST': HOSTS['REDIS'],
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
        'rest_framework.authentication.TokenAuthentication',
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

# AWS Credentials
AWS_ACCESS_KEY_ID = 'AKIAIVT4H6LXT37KKDQQ'
AWS_SECRET_ACCESS_KEY = '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'

# S3 Config
AWS_STORAGE_BUCKET_NAME = "%s-storage" % PROJECT_NAME
AWS_HEADERS = {
    'Expires': 'Thu, 15 Apr 2020 20:00:00 GMT',
    'Cache-Control': 'max-age=2592000',
}

# EC2 Config
EC2_REGION = 'eu-central-1'
EC2_INSTANCE_TYPE = 't2.micro'
EC2_AMI = 'ami-accff2b1'
EC2_KEY_PAIR_DIR = "%s/app/conf" % BASE_DIR
EC2_KEY_PAIR = "%s/%s.pem" % (EC2_KEY_PAIR_DIR, PROJECT_NAME)
EC2_SERVER_USERNAME = 'ubuntu'

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
