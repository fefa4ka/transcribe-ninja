#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf import settings
from django.conf.urls import patterns, url, include
from django.contrib import admin

from rest_framework.urlpatterns import format_suffix_patterns


admin.autodiscover()

urlpatterns = patterns(
    '',
    (r'^admin/', include(admin.site.urls)),
)

# В продакшене фронтенд отдаёт NGINX
if settings.DEBUG:
    urlpatterns += patterns(
        'django.contrib.staticfiles.views',
        url(r'^(?:index.html)?$', 'serve', kwargs={'path': 'index.html'}),
        url(r'^(?P<path>(?:js|css|img|data)/.*)$', 'serve'),
    )

urlpatterns = format_suffix_patterns(urlpatterns)
