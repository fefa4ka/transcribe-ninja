#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.contrib.admin import ModelAdmin
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType

from work.models import Payment, Order, Queue
from transcribe.models import Record

from site import admin_site


# class PaymentAdmin(ModelAdmin):
#     list_display = ('price', 'amount', 'total', 'owner',  'object_link', 'comment', 'created')

#     list_filter = ('content_type', 'status')

#     fieldsets = (
#         ('Payment for', {
#             'classes': ('collapse',),
#             'fields': ('content_type', 'object_id')
#         }),
#         ('Total', {
#             'fields': ('price', 'amount', 'total', 'comment', 'destination')
#         }),
#         ('Status', {
#             'classes': ('collapse',),
#             'fields': ('owner', 'status')
#         }),
#     )

#     readonly_fields = ('amount',)

#     search_fields = ['owner__username']

#     def object_link(self, instance):
#         obj = instance.content_object
#         ct = instance.content_type
#         if type(instance.content_object) in [Queue, Order]:
#             if type(instance.content_object) == Order:
#                 ct = ContentType.objects.get_for_model(Record)
#                 obj = instance.content_object.record

#             url = reverse('admin:%s_%s_change' % (ct.app_label, ct.model), args=(obj.id,))
#             return '<a href="%s">%s</a>' % (url, obj)
#         else:
#             return obj

#     object_link.allow_tags = True

#     def amount(self, instance):
#         if type(instance.content_object) == Queue:
#             return instance.content_object.work_length

#         if type(instance.content_object) == Order:
#             return instance.content_object.end_at - instance.content_object.start_at


# admin_site.register(Payment, PaymentAdmin)

class Salary(Payment):
    pass

class SalaryAdmin(ModelAdmin):
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

        qs = super(SalaryAdmin, self).get_queryset(request)

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
        return super(SalaryAdmin,self).changelist_view(request, extra_context=extra_context)


admin_site.register(Payment, SalaryAdmin)
