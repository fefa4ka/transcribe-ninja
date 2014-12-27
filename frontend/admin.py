#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib import admin

from core.models import *
from transcribe.models import *
from order.models import *


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
        return instance.transcriptions.count()




admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class PieceInline(admin.TabularInline):
    model = Piece
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


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('record', 'owner', 'duration', 'total', 'completed')
    fieldsets = (
        (None, {
            'fields': ('record', 'start_at', 'end_at')
        }),
        ('Payment information', {
            'fields': ('price', 'owner')
        }),
    )

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

@admin.register(Queue)
class QueueAdmin(admin.ModelAdmin):
    list_display = ('record', 'start_at', 'end_at', 'duration', 'work_type', 'priority')
    list_filter = ('priority', 'work_type')

    def record(self, instance):
        return instance.piece.record

    def duration(self, instance):
        return instance.end_at() - instance.start_at()

    def has_add_permission(self, request):
        return False
