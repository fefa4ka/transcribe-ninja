#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib import admin

from backend.transcribe.models import *
from backend.order.models import *

class PieceInline(admin.StackedInline):
    model = Piece
    extra = 3


class RecordAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['title']})
    ]
    inlines = [PieceInline]

admin.site.register(Record, RecordAdmin)

class PriceAdmin(admin.ModelAdmin):
    pass

admin.site.register(Price, PriceAdmin)
