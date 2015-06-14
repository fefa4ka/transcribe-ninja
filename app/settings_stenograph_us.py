#!/usr/bin/python
# -*- coding: utf-8 -*-

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from settings import *

DOMAIN = 'stenograph.us'

EMAIL_HOST_USER = DEFAULT_FROM_EMAIL = "info@stenographus.ru"

WSGI_APPLICATION = "app.wsgi_%s.application" % DOMAIN.replace(".", "_")

#
# Auth
#
DJOSER = {
    'DOMAIN': DOMAIN,
    'SITE_NAME': 'Stenograph.us',
    'PASSWORD_RESET_CONFIRM_URL': '#/password/reset/confirm/{uid}/{token}',
    'ACTIVATION_URL': '#/activate/{uid}/{token}',
    'LOGIN_AFTER_ACTIVATION': True,
    'SEND_ACTIVATION_EMAIL': True,
}

# Google Oauth2
GOOGLE_API_KEY = 'AIzaSyC6CGz9s-XTNsIZd5JaowVG0oU8dJvTkTg'
GOOGLE_OAUTH2_CLIENT_ID = '921357859645-h0fg781d5146ou0r2q489m7p6v3d7p82.apps.googleusercontent.com'
GOOGLE_OAUTH2_CLIENT_SECRET = 'xoav0fs5Rc7P2nhZeKojnJPd'

# Facebook API
FACEBOOK_APP_ID              = '844469605608962'
FACEBOOK_API_SECRET          = '01dea69bc9ab160f8615b56a9604f26c'
FACEBOOK_EXTENDED_PERMISSIONS = ['email']

# VK Api
VK_APP_ID = '4953708'
VK_API_SECRET = 'DPuBGWwzZioNYexUYKJx'
# VK_EXTRA_SCOPE = ['email']


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, "static/%s/" % DOMAIN)

if DEBUG:
    FRONTEND_ROOT = os.path.join(BASE_DIR, "frontend/%s/build/" % DOMAIN)
    STATICFILES_DIRS = (
        FRONTEND_ROOT,
        os.path.join(BASE_DIR, "frontend/%s/bin/" % DOMAIN),
    )

STATIC_URL = '/static/'
