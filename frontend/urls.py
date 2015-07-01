#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf import settings
from django.conf.urls import patterns, url

from rest_framework.urlpatterns import format_suffix_patterns

# В продакшене фронтенд отдаёт NGINX
if not settings.PROD and settings.DEBUG:
    urlpatterns = patterns(
        'django.contrib.staticfiles.views',
        url(r'^(?:index.html)?$', 'serve', kwargs={'path': 'index.html'}),
        url(r'^(?P<path>(?:js|css|img|data)/.*)$', 'serve'),
    )

urlpatterns = format_suffix_patterns(urlpatterns)
