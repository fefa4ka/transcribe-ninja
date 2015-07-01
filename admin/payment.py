#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.contrib.admin import ModelAdmin

from work.models import Payment, Order, Queue

from site import admin_site


class PaymentAdmin(ModelAdmin):
    list_display = ('content_object', 'price', 'total', 'amount', 'owner', 'created')

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

    def amount(self, instance):
        if type(instance.content_object) == Queue:
            return instance.content_object.work_length

        if type(instance.content_object) == Order:
            return instance.content_object.end_at - instance.content_object.start_at

    def has_add_permission(self, request):
        return False

admin_site.register(Payment, PaymentAdmin)
