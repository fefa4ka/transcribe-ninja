#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.contrib.admin import ModelAdmin
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType

from work.models import Payment, Order, Queue
from transcribe.models import Record

from site import admin_site


class PaymentAdmin(ModelAdmin):
    list_display = ('price', 'amount', 'total', 'owner',  'object_link', 'comment', 'created')

    list_filter = ('content_type', 'status')

    fieldsets = (
        ('Payment for', {
            'classes': ('collapse',),
            'fields': ('content_type', 'object_id')
        }),
        ('Total', {
            'fields': ('price', 'amount', 'total', 'comment', 'destination')
        }),
        ('Status', {
            'classes': ('collapse',),
            'fields': ('owner', 'status')
        }),
    )

    readonly_fields = ('amount',)

    search_fields = ['owner__username']

    def object_link(self, instance):
        obj = instance.content_object
        ct = instance.content_type
        if type(instance.content_object) in [Queue, Order]:
            if type(instance.content_object) == Order:
                ct = ContentType.objects.get_for_model(Record)
                obj = instance.content_object.record

            url = reverse('admin:%s_%s_change' % (ct.app_label, ct.model), args=(obj.id,))
            return '<a href="%s">%s</a>' % (url, obj)
        else:
            return obj

    object_link.allow_tags = True

    def amount(self, instance):
        if type(instance.content_object) == Queue:
            return instance.content_object.work_length

        if type(instance.content_object) == Order:
            return instance.content_object.end_at - instance.content_object.start_at


admin_site.register(Payment, PaymentAdmin)
