#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf.urls import url, include

urlpatterns = (
    url(r'^', include('api.urls')),
    url(r'^', include('frontend.urls'))
)
