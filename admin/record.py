#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.contrib.contenttypes.models import ContentType
from django.forms import ModelForm
from django.forms.models import BaseInlineFormSet
from django.contrib.admin import ModelAdmin, TabularInline
from django.db.models import Sum

from transcribe.models import Record, Piece
from work.models import Payment, Order, Queue

import core.async_jobs

from site import admin_site



# class PieceInline(TabularInline):
#     model = Piece
#     formset = PieceFormSet
#     extra = 0


class RecordForm(ModelForm):

    class Meta:
        model = Record
        exclude = ['language']


def analys(modeladmin, request, queryset):
    """
        Режем на куски, если не порезано
    """
    for record in queryset.all():
        core.async_jobs.record_analys.delay(record)


class RecordAdmin(ModelAdmin):
    list_display = ('title', 'duration', 'total_price', 'spent_money', 'progress', 'completed', 'work_length', 'owner')

    form = RecordForm

    fieldsets = (
        (None, {
            'fields': ('audio_file', 'title', 'owner')
        }),
        ('Recod properties', {
            'classes': ('collapse',),
            'fields': ('speakers', 'duration', 'progress')
        }),
        ('Transcribe info', {
            'classes': ('collapse',),
            'fields': ('completed', 'work_length', 'mistakes_length', 'pieces_count', 'completed_transcribe', 'completed_check')
        }),
        ('Payments info', {
            'classes': ('collapse',),
            'fields': ('total_price', 'spent_money', 'spent_money_yandex', 'spent_money_transcribe', 'spent_money_check')
        })

    )

    readonly_fields = ('pieces_count', 'completed', 'completed_transcribe', 'completed_check', 'work_length', 'mistakes_length', 'total_price', 'spent_money', 'spent_money_yandex', 'spent_money_transcribe', 'spent_money_check',)

    search_fields = ['title', 'owner__username']

    actions = [analys]

    # inlines = [PieceInline]

    def pieces_count(self, instance):
        return instance.pieces.count()

    def total_price(self, instance):
        order_object_id = ContentType.objects.get_for_model(Order).id

        payment = 0
        for order in instance.orders.all():
            payment += Payment.objects.get(content_type_id=order_object_id, object_id=order.id).total

        return round(payment, 1)

    def spent_money(self, instance):
        return self.spent_money_transcribe(instance) + self.spent_money_check(instance)

    def spent_money_yandex(self, instance):
        amount = 0
        for order in instance.orders.all():
            amount += order.spent_money(work_type=0, owner_id=2) or 0

        return amount

    def spent_money_transcribe(self, instance):
        amount = 0
        for order in instance.orders.all():
            amount += order.spent_money(work_type=0) or 0
        return amount

    def spent_money_check(self, instance):
        amount = 0
        for order in instance.orders.all():
            amount += order.spent_money(work_type=1) or 0
        return amount


    def work_length(self, instance):
        amount = 0
        for order in instance.orders.all():
            queue_length = Queue.objects.filter(order=order, completed__isnull=False).aggregate(Sum('work_length'))
            amount += queue_length["work_length__sum"]
        return amount

    def mistakes_length(self, instance):
        amount = 0
        for order in instance.orders.all():
            queue_length = Queue.objects.filter(order=order, completed__isnull=False).aggregate(Sum('mistakes_length'))
            amount += queue_length["mistakes_length__sum"]
        return amount


    def completed_transcribe(self, instance):
        amount = 0
        for order in instance.orders.all():
            amount += order.queue.filter(work_type=0, completed__isnull=False).count()
        return amount

    def completed_check(self, instance):
        amount = 0
        for order in instance.orders.all():
            amount += order.queue.filter(work_type=1, completed__isnull=False).count()
        return amount


admin_site.register(Record, RecordAdmin)
