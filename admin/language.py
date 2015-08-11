#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.contrib.admin import ModelAdmin

from core.models import Language

from site import admin_site


class LanguageAdmin(ModelAdmin):
    list_display = ('code', 'name', 'english_name')

admin_site.register(Language, LanguageAdmin)
