#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.contrib.admin import ModelAdmin
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum

from work.models import Payment, Order, Queue

from site import admin_site


class OrderAdmin(ModelAdmin):
    list_display = ('record', 'owner', 'duration', 'length', 'total', 'spent_money', 'spent_money_yandex', 'spent_money_transcribe', 'spent_money_check', 'transcribe_completed', 'check_completed')
    fieldsets = (
        (None, {
            'fields': ('record', 'start_at', 'end_at', 'transcribe_completed', 'check_completed')
        }),
        ('Payment information', {
            'fields': ( 'total', 'spent_money', 'spent_money_transcribe', 'spent_money_check', 'price', 'owner')
        }),
    )


    def has_add_permission(self, request):
        return False

    def duration(self, instance):
        return instance.end_at - instance.start_at

    def length(self, instance):
        length = Queue.objects.filter(order=instance, completed__isnull=False).aggregate(Sum('work_length'))
        return length["work_length__sum"]

    def total(self, instance):
        order_object_id = ContentType.objects.get_for_model(Order).id
        payment = Payment.objects.get(content_type_id=order_object_id, object_id=instance.id)

        return payment.total

    def spent_money(self, instance):
        return self.spent_money_transcribe(instance) + self.spent_money_check(instance)

    def spent_money_yandex(self, instance):
        return instance.spent_money(work_type=0, owner_id=2) or 0

    def spent_money_transcribe(self, instance):
        return instance.spent_money(work_type=0) or 0

    def spent_money_check(self, instance):
        return instance.spent_money(work_type=1) or 0

    def transcribe_completed(self, instance):
        return round(instance.completed_percentage(work_type=0))

    def check_completed(self, instance):
        return round(instance.completed_percentage(work_type=1))

admin_site.register(Order, OrderAdmin)

