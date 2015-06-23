#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib import admin

from core.models import *
from transcribe.models import *
from work.models import *


# class UserAdmin(admin.ModelAdmin):
#     list_display = ('email', 'first_name', 'last_name')
#     list_filter = ('is_staff', 'is_superuser')


# class UserAccoundAdmin(admin.StackedInline):
#     model = Account

# print dir(admin.ModelAdmin)


# class ExtendedUserAdmin(admin.ModelAdmin):
#     inlines = UserAdmin.inlines + (UserAccoundAdmin,)

# admin.site.unregister(User)
# admin.site.register(User, UserAdmin)

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

import numpy as np


class AccountInline(admin.StackedInline):
    model = Account

    def speed(self, instance, work_type):
        durations = []
        time_spent = []
        speed = []

        for queue in instance.user.queue.filter(completed__isnull=False, work_type__exact=work_type):
            spent = (queue.completed - queue.locked).total_seconds()
            durations.append(queue.duration)
            time_spent.append(spent)

            if work_type == 0:
                length = len(queue.transcription)
                # Скорость знаков в минуту
                speed.append(length * 60 / spent )
            else:
                # Скорость измеряется в коээфициенте на которое умнажается время записи
                speed.append(spent / queue.duration)

        return np.mean(speed)

    def transcribe_speed(self, instance):
        return self.speed(instance, 0)

    def check_speed(self, instance):
        return self.speed(instance, 1)



class UserAdmin(UserAdmin):
    list_display = ( 'username', 'first_name', 'last_name', 'balance', 'work_length', 'mistakes_part', 'transcribe_count', 'check_count')
    list_filter = ('last_login', 'date_joined')

    inlines = (AccountInline,)

    def balance(self, instance):
        queue_object_id = ContentType.objects.get_for_model(Queue).id
        order_object_id = ContentType.objects.get_for_model(Order).id

        if instance.account.site == "transcribe.ninja":
            object_id = queue_object_id
        else:
            object_id = order_object_id

        for balance in instance.account.balances:
            if balance['content_type_id'] == object_id:
                return balance["total"] or 0

        return 0

    def work_length(self, instance):
        return instance.queue.all().aggregate(lenght=Sum('work_length'))["lenght"] or 0

    def mistakes_part(self, instance):
        mistakes_length = instance.queue.all().aggregate(lenght=Sum('mistakes_length'))["lenght"] or 0
        work_length = self.work_length(instance)

        if work_length > 0:
            mistakes_part = round(mistakes_length / float(self.work_length(instance)), 2)
        else:
            mistakes_part = 0

        return mistakes_part

    def records_count(self, instance):
        return instance.records.count()

    def transcribe_count(self, instance):
        # Считаем количество выполненныех очередей на распознание
        return instance.queue.filter(work_type__exact=0).count()

    def check_count(self, instance):
        # Считаем количество выполненныех очередей на распознание
        return instance.queue.filter(work_type__exact=1).count()


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class PieceInline(admin.TabularInline):
    model = Piece
    extra = 0


class TranscriptionInline(admin.TabularInline):
    model = Transcription
    extra = 0

@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = ('title', 'duration', 'speakers', 'pieces', 'progress', 'completed', 'owner')

    fieldsets = (
        (None, {
            'fields': ('audio_file', 'title', 'owner')
        }),
        ('Recod properties', {
            'classes': ('collapse',),
            'fields': ('speakers', 'duration', 'progress')
        }),
    )

    inlines = [PieceInline]

    def pieces(self, instance):
        return instance.pieces.count()


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ('title', 'content_type', 'price')



class QueueInline(admin.TabularInline):
    model = Queue
    extra = 0

    # TODO: В элементе очереди отображать только 


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('record', 'owner', 'duration', 'total', 'spent_money', 'spent_money_transcribe', 'spent_money_check', 'transcribe_completed', 'check_completed')
    fieldsets = (
        (None, {
            'fields': ('record', 'start_at', 'end_at', 'transcribe_completed', 'check_completed')
        }),
        ('Payment information', {
            'fields': ( 'total', 'spent_money', 'spent_money_transcribe', 'spent_money_check', 'price', 'owner')
        }),
    )

    readonly_fields = ('total', 'spent_money', 'transcribe_completed', 'check_completed')

    inlines = [QueueInline]

    def has_add_permission(self, request):
        return False

    def duration(self, instance):
        return instance.end_at - instance.start_at

    def total(self, instance):
        order_object_id = ContentType.objects.get_for_model(Order).id
        payment = Payment.objects.get(content_type_id=order_object_id, object_id=instance.id)

        return payment.total

    def spent_money(self, instance):
        return instance.spent_money(work_type=0) + instance.spent_money(work_type=1)

    def spent_money_transcribe(self, instance):
        return instance.spent_money(work_type=0)

    def spent_money_check(self, instance):
        return instance.spent_money(work_type=1)

    def transcribe_completed(self, instance):
        return round(instance.completed_percentage(work_type=0))

    def check_completed(self, instance):
        return round(instance.completed_percentage(work_type=1))

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('content_object', 'owner', 'price', 'total', 'status', 'created')
    list_filter = ('content_type', 'status')

    fieldsets = (
        ('Payment for', {
            'fields': ('content_type', 'object_id')
        }),
        ('Total', {
            'fields': ('price', 'total')
        }),
        ('Status', {
            'fields': ('owner', 'status')
        }),
    )

    def has_add_permission(self, request):
        return False


@admin.register(Queue)
class QueueAdmin(admin.ModelAdmin):
    list_display = ('id', 'record', 'work_type', 'duration', 'owner', 'total_price', 'work_length', 'mistakes_length', 'locked', 'completed', 'checked', 'priority', 'skipped')
    list_filter = ('priority', 'work_type', 'locked', 'completed', 'checked')

    readonly_fields = ('total_price', 'work_length', 'mistakes_length', 'original_transcription', 'transcription', 'checked_transcription')

    fieldsets = (
        (None, {
            'fields': ('order', 'piece', 'audio_file')
        }),
        ('Result', {
            'fields': ('original_transcription', 'transcription', 'checked_transcription')
        }),
        ('Work and payment information', {
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
