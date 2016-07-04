#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf import settings
from django.conf.urls import url, include, patterns

from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = (
    url(r'^', include('api.urls')),
    url(r'^', include('admin.urls')),
)
