#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf.urls import url, include, patterns
from django.conf import settings
import django.views.static

import django_rq.urls 

urlpatterns = (
    url(r'^', include('backend.api.urls')),
    url(r'^', include('backend.web.urls')),
    url(r'^django-rq/', include('django_rq.urls'))
)
