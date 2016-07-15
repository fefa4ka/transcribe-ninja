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

SITE_ID = 1

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '@0jnn4oh3h2ri-y6skgfea!&07o+5z8#oamzh-1nmm)wq*p(e%'

PROJECT_NAME = 'stenograph-us'

EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_HOST_PASSWORD = 'cntyjuhfa,kznm'
EMAIL_PORT = 587
EMAIL_USE_TLS = True


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
PROD = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

PROJECT_DIR = '~/' + PROJECT_NAME
ENV_DIR = '%s/env' % PROJECT_DIR
LOGS_DIR = '~/logs'
ACTIVATE = '. %s/bin/activate' % ENV_DIR

REPOSITORY = 'git@github.com:fefa4ka/transcribe-ninja.git'
GIT_USERNAME = 'fefa4ka'
ADMIN_EMAIL = 'fefa4ka@gmail.com'
GIT_KEY_PATH = '/Users/fefa4ka/.ssh/deploy_rsa'
GIT_KEY_NAME = 'github_rsa'

YANDEX_API_KEY = 'aa0f1865-e414-42d2-9c50-cff9a64743a0'
UUID = '12345A781234567B1234567812345678'


# Application definition
INSTALLED_APPS = (
    # 'bootstrap_admin',
    'wpadmin',
    'django.contrib.admin',
    'django_rq_dashboard',

    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',


    # Core
    'core',
    'transcribe',
    'work',
    'django_rq',

    # Mailing
    'django_mailbox',
    'dbmail',

    # API
    'rest_framework',
    'rest_framework.authtoken',
    'api',

    # Web
    'social_auth',
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

#
#
#
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'social_auth.context_processors.social_auth_by_name_backends',
)

TEMPLATE_DIRS = (os.path.join(BASE_DIR, "../admin/templates/"),
    os.path.join(BASE_DIR, "../api/account/templates/"),
)


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

SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/#/auth-complete'

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
        'DB': 0,
        'PASSWORD': '',
        'DEFAULT_TIMEOUT': 360,
    },
    # Split audio
    'make_queue': {
        'HOST': HOSTS['REDIS'],
        'PORT': 6379,
        'DB': 0,
        'PASSWORD': '',
        'DEFAULT_TIMEOUT': 360,
    },
    'update_queue': {
        'HOST': HOSTS['REDIS'],
        'PORT': 6379,
        'DB': 0,
        'PASSWORD': '',
        'DEFAULT_TIMEOUT': 360,
    }
}

RQ = {
    'host': HOSTS['REDIS'],
    'port': 6379,
    'db': 0,
    'password': None,
    'socket_timeout': None,
    'connection_pool': None,
    'charset': 'utf-8',
    'errors': 'strict',
    'decode_responses': False,
    'unix_socket_path': None,
}

# CACHES = {
#     "default": {
#         'BACKEND': 'redis_cache.cache.RedisCache',
#         'LOCATION': '%s:6379:2' % HOSTS['REDIS'],
#     },
# }

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
EC2_INSTANCE_TYPE = 't2.medium'
EC2_AMI = 'ami-accff2b1'
EC2_KEY_PAIR_DIR = "%s/app/conf" % BASE_DIR
EC2_KEY_PAIR = "%s/%s.pem" % (EC2_KEY_PAIR_DIR, PROJECT_NAME)
EC2_SERVER_USERNAME = 'ubuntu'

# Media content
MEDIA_ROOT = os.path.join(BASE_DIR, "../../data/media/")

# Records content
RECORD_ROOT = os.path.join(MEDIA_ROOT, "record/")
PIECE_ROOT = os.path.join(MEDIA_ROOT, "piece/")

TEMP_DIR = os.path.join(BASE_DIR, "temp/")

STATIC_URL = '/static/'

#
# Record
#

# Подсчёт скорости разговора
# Средняя скорость произношения. Знаков в секунду
SPEECH_SPEED = 22

# Сколько минимум записи должно быть распознано,
# чтобы посчтитать скорость произоншения
SPEECH_SPEED_MIN_DURATION = 120

# После скольки раз считать запись неразборчивой
SPEECH_POOR_LIMIT = 3

# Одновременно распознаётся
RECORDS_ONAIR = 2

# На какие куски делить запись при диаризации
DIARIZATION_PART_SIZE = 10.00

# ADMIN
WPADMIN = {
    'admin': {
        'admin_site': 'admin.site.admin_site',
        'title': 'Divide and conquer',
        'menu': {
            'top': 'admin.menu.TopMenu',
            'left': 'wpadmin.menu.menus.BasicLeftMenu',
        },
        'dashboard': {
            'breadcrumbs': True,
        },
        'custom_style': STATIC_URL + 'wpadmin/css/themes/light.css',
    }
}