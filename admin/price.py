#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.contrib.admin import ModelAdmin

from work.models import Price

from site import admin_site


class PriceAdmin(ModelAdmin):
    list_display = ('title', 'content_type', 'price')

admin_site.register(Price, PriceAdmin)
