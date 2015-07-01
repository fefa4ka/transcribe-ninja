#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include
from admin import admin_site

urlpatterns = patterns(
    '',
    (r'^admin/', include(admin_site.urls)),
    (r'^admin/rq/', include('django_rq_dashboard.urls')),
)
