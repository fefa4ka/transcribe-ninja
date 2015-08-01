#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.contrib.admin import ModelAdmin

from core.models import Feedback

from site import admin_site


class FeedbackAdmin(ModelAdmin):
    list_display = ('email', 'phone', 'subject')

admin_site.register(Feedback, FeedbackAdmin)
