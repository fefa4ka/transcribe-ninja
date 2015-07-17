#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.contrib.admin import ModelAdmin
from django.core.urlresolvers import reverse

from work.models import Payment, Order, Queue

from site import admin_site


class PaymentAdmin(ModelAdmin):
    list_display = ('content_object', 'price', 'total', 'amount', 'owner', 'object_link', 'created')

    list_filter = ('content_type', 'status')

    fieldsets = (
        ('Payment for', {
            'fields': ('content_type', 'object_id')
        }),
        ('Total', {
            'fields': ('price', 'amount', 'total')
        }),
        ('Status', {
            'fields': ('owner', 'status')
        }),
    )

    readonly_fields = ('amount',)

    search_fields = ['owner__username']

    def object_link(self, instance):
        obj = instance.content_object
        ct = instance.content_type
        if  type(instance.content_object) == Queue:
            url = reverse('admin:%s_%s_change' % (ct.app_label, ct.model), args=(obj.id,))
            return '<a href="%s">%s</a>' % (url, obj.id)
        else:
            return obj

    object_link.allow_tags = True

    def amount(self, instance):
        if type(instance.content_object) == Queue:
            return instance.content_object.work_length

        if type(instance.content_object) == Order:
            return instance.content_object.end_at - instance.content_object.start_at


admin_site.register(Payment, PaymentAdmin)
