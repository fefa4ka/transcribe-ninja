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


class AccountInline(admin.StackedInline):
    model = Account


class UserAdmin(UserAdmin):
    list_display = ( 'email', 'first_name', 'last_name', 'balance', 'records_count', 'transcriptions_count')

    inlines = (AccountInline,)

    def balance(self, instance):
        return instance.account.balance

    def records_count(self, instance):
        return instance.records.count()

    def transcriptions_count(self, instance):
        # Считаем количество выполненныех очередей на распознание
        return instance.queue.filter(work_type__exact=0).count()


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

    def completed(self, instance):
        return instance.completed_percentage()

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
    list_display = ('record', 'owner', 'duration', 'total', 'completed')
    fieldsets = (
        (None, {
            'fields': ('record', 'start_at', 'end_at', 'completed')
        }),
        ('Payment information', {
            'fields': ( 'total', 'price', 'owner')
        }),
    )

    readonly_fields = ('total', 'completed')

    inlines = [QueueInline]

    def has_add_permission(self, request):
        return False

    def duration(self, instance):
        return instance.end_at - instance.start_at

    def total(self, instance):
        order_object_id = ContentType.objects.get_for_model(Order).id
        payment = Payment.objects.get(content_type_id=order_object_id, object_id=instance.id)

        return payment.total

    def completed(self, instance):
        return instance.record.completed_percentage()


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
    list_display = ('record', 'start_at', 'end_at', 'duration', 'work_type', 'priority', 'skipped', 'locked', 'owner')
    list_filter = ('priority', 'work_type', 'locked')

    fieldsets = (
        (None, {
            'fields': ('order', 'piece', 'audio_file')
        }),
        ('Work and payment information', {
            'fields': ('price', 'work_type', 'priority')
        }),
        ('Worker', {
            'fields': ('owner', 'locked', 'completed')
        }),
    )

    inlines = [TranscriptionInline]

    def record(self, instance):
        return instance.piece.record

    def duration(self, instance):
        return instance.end_at() - instance.start_at()

    def has_add_permission(self, request):
        return False
