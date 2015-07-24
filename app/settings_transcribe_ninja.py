#!/usr/bin/python
# -*- coding: utf-8 -*-

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from settings_production import *

DOMAIN = 'transcribe.ninja'

EMAIL_HOST_USER = DEFAULT_FROM_EMAIL = 'info@transcribe.ninja'

WSGI_APPLICATION = 'app.wsgi_%s.application' % DOMAIN.replace(".", "_")

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


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, "static/%s/" % DOMAIN)

if not PROD and DEBUG:
    STATICFILES_DIRS = (
        os.path.join(BASE_DIR, "frontend/%s/build/" % DOMAIN),
    )
else:
    STATICFILES_DIRS = (
        os.path.join(BASE_DIR, "frontend/%s/bin/" % DOMAIN),
    )



LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'transcribe_ninja.log',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers':['file'],
            'propagate': True,
            'level': 'WARNING',
        },
        'api': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
    }
}