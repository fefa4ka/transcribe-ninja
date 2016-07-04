#!/usr/bin/python
# -*- coding: utf-8 -*-

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from .development import *

DOMAIN = 'stenograph.us'

EMAIL_HOST_USER = "info@stenograph.us"
DEFAULT_FROM_EMAIL = u"Стеня Графов <info@stenograph.us>"

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

# Yandex.Money
YANDEX_MONEY_DEBUG = True
YANDEX_MONEY_SCID = 12345
YANDEX_MONEY_SHOP_ID = 47394
YANDEX_MONEY_SHOP_PASSWORD = 'password'
YANDEX_MONEY_FAIL_URL = 'http://stenograph.us/#/payments/fail-payment/'
YANDEX_MONEY_SUCCESS_URL = 'http://stenograph.us/#/payments/success-payment/'
YANDEX_MONEY_MAIL_ADMINS_ON_PAYMENT_ERROR = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/
# Paths relative to settings file
STATIC_ROOT = os.path.join(BASE_DIR, "../../static/%s/" % DOMAIN)

if not PROD and DEBUG:
    STATICFILES_DIRS = (
        os.path.join(BASE_DIR, "../../frontend/%s/build/" % DOMAIN),
        os.path.join(BASE_DIR, "admin/static/"),
    )
else:
    STATICFILES_DIRS = (
        os.path.join(BASE_DIR, "../../frontend/%s/bin/" % DOMAIN),
        os.path.join(BASE_DIR, "admin/static/"),
    )

