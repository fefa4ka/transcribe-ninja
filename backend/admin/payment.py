#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.contrib.admin import ModelAdmin
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType

from work.models import Payment, Order, Queue
from transcribe.models import Record

from site import admin_site


class PaymentAdmin(ModelAdmin):
    list_display = ('comment','destination', 'total', 'owner', 'status', 'created')

    list_filter = ('comment', 'status')

    fieldsets = (
        ('Payment for', {
            'classes': ('collapse',),
            'fields': ('content_type', 'object_id')
        }),
        ('Total', {
            'fields': ('price', 'total', 'comment', 'destination', 'owner', 'status')
        })
    )

    search_fields = ['owner__username']

    def get_queryset(self, request):
        from work.models import Account

        qs = super(PaymentAdmin, self).get_queryset(request)

        account_object_id = ContentType.objects.get_for_model(Account).id

        return qs.filter(content_type_id=account_object_id)

    def changelist_view(self, request, extra_context=None):
        # referer = request.META.get('HTTP_REFERER', '')
        # showall = request.META['PATH_INFO'] in referer and not request.GET.has_key('status')
        # if not showall and not request.GET.has_key('param_name_here'):
        if not request.GET.has_key('status__exact'):
            q = request.GET.copy()
            q['status__exact'] = '0'
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()
        return super(PaymentAdmin,self).changelist_view(request, extra_context=extra_context)


admin_site.register(Payment, PaymentAdmin)
