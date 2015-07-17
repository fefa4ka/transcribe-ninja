#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.contrib.admin import ModelAdmin
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin import TabularInline

from work.models import Queue, Transcription

from site import admin_site


class TranscriptionInline(TabularInline):
    model = Transcription
    extra = 0


class QueueAdmin(ModelAdmin):
    list_display = ('id', 'record', 'work_type', 'duration', 'owner', 'total_price', 'work_length', 'mistakes_length', 'locked', 'completed', 'checked', 'priority', 'skipped')
    list_filter = ('priority', 'work_type', 'locked', 'completed', 'checked')

    readonly_fields = ('total_price', 'work_length', 'mistakes_length', 'original_transcription', 'transcription', 'checked_transcription')

    fieldsets = (
        (None, {
            'classes': ('collapse',),
            'fields': ('order', 'piece', 'audio_file')
        }),
        ('Result', {
            'fields': ('original_transcription', 'transcription', 'checked_transcription')
        }),
        ('Work and payment information', {
            'classes': ('collapse',),
            'fields': ('total_price', 'price', 'work_type', 'work_length', 'mistakes_length', 'priority')
        }),
        ('Worker', {
            'classes': ('collapse',),
            'fields': ('owner', 'locked', 'completed')
        })
    )

    inlines = [TranscriptionInline]

    def record(self, instance):
        return instance.piece.record

    def duration(self, instance):
        return instance.end_at - instance.start_at

    def total_price(self, instance):
        queue_object_id = ContentType.objects.get_for_model(Queue).id

        try:
            payment = Payment.objects.get(content_type_id=queue_object_id, object_id=instance.id)

            return payment.total
        except:
            return 0

    def has_add_permission(self, request):
        return False

admin_site.register(Queue, QueueAdmin)
