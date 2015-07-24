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
    exclude = ['speaker']


class QueueAdmin(ModelAdmin):
    list_display = ('work_type', 'duration', 'owner', 'total_price', 'work_length', 'mistakes_length', 'record', 'completed', 'checked')
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
            'fields': ('total_price', 'price', 'work_type', 'work_length', 'mistakes_length', 'priority', 'poored')
        }),
        ('Worker', {
            'classes': ('collapse',),
            'fields': ('owner', 'locked', 'completed')
        })
    )

    inlines = [TranscriptionInline]

    ordering = ('-completed', )

    def record(self, instance):
        return instance.piece.record

    def duration(self, instance):
        return instance.end_at - instance.start_at

    def total_price(self, instance):
        from work.models import Payment
        queue_object_id = ContentType.objects.get_for_model(Queue).id

        try:
            payment = Payment.objects.get(content_type_id=queue_object_id, object_id=instance.id)

            return payment.total
        except:
            return 0

    def has_add_permission(self, request):
        return False

   # def get_queryset(self, request):
   #      from work.models import Account

   #      qs = super(SalaryAdmin, self).get_queryset(request)

   #      account_object_id = ContentType.objects.get_for_model(Account).id

   #      return qs.filter(content_type_id=account_object_id)

    def changelist_view(self, request, extra_context=None):
        # referer = request.META.get('HTTP_REFERER', '')
        # showall = request.META['PATH_INFO'] in referer and not request.GET.has_key('status')
        # if not showall and not request.GET.has_key('param_name_here'):
        if not request.GET.has_key('completed_gte'):
            q = request.GET.copy()
            q['completed__isnull'] = '0'
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()
        return super(QueueAdmin,self).changelist_view(request, extra_context=extra_context)

admin_site.register(Queue, QueueAdmin)
# 