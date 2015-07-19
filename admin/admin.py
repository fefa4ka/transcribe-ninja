#!/usr/bin/python
# -*- coding: utf-8 -*-

from account import *
from record import *
from payment import *
from queue import *
from price import *
# from order import *



# class TranscriptionInline(admin.TabularInline):
#     model = Transcription
#     extra = 0



# @admin.register(Price)
# class PriceAdmin(admin.ModelAdmin):
#     list_display = ('title', 'content_type', 'price')



# class QueueInline(admin.TabularInline):
#     model = Queue
#     extra = 0

#     # TODO: В элементе очереди отображать только 


# @admin_site.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     list_display = ('record', 'owner', 'duration', 'length', 'total', 'spent_money', 'spent_money_yandex', 'spent_money_transcribe', 'spent_money_check', 'transcribe_completed', 'check_completed')
#     fieldsets = (
#         (None, {
#             'fields': ('record', 'start_at', 'end_at', 'transcribe_completed', 'check_completed')
#         }),
#         ('Payment information', {
#             'fields': ( 'total', 'spent_money', 'spent_money_transcribe', 'spent_money_check', 'price', 'owner')
#         }),
#     )

#     readonly_fields = ('total', 'spent_money', 'transcribe_completed', 'check_completed')

#     inlines = [QueueInline]

#     def has_add_permission(self, request):
#         return False

#     def duration(self, instance):
#         return instance.end_at - instance.start_at

#     def length(self, instance):
#         length = Queue.objects.filter(order=instance, completed__isnull=False).aggregate(Sum('work_length'))
#         return length["work_length__sum"]

#     def total(self, instance):
#         order_object_id = ContentType.objects.get_for_model(Order).id
#         payment = Payment.objects.get(content_type_id=order_object_id, object_id=instance.id)

#         return payment.total

#     def spent_money(self, instance):
#         return self.spent_money_transcribe(instance) + self.spent_money_check(instance)

#     def spent_money_yandex(self, instance):
#         return instance.spent_money(work_type=0, owner_id=2) or 0

#     def spent_money_transcribe(self, instance):
#         return instance.spent_money(work_type=0) or 0

#     def spent_money_check(self, instance):
#         return instance.spent_money(work_type=1) or 0

#     def transcribe_completed(self, instance):
#         return round(instance.completed_percentage(work_type=0))

#     def check_completed(self, instance):
#         return round(instance.completed_percentage(work_type=1))

# @admin_site.register(Payment)
# class PaymentAdmin(admin.ModelAdmin):
#     list_display = ('content_object', 'owner', 'price', 'total', 'status', 'created')
#     list_filter = ('content_type', 'status')

#     fieldsets = (
#         ('Payment for', {
#             'fields': ('content_type', 'object_id')
#         }),
#         ('Total', {
#             'fields': ('price', 'total')
#         }),
#         ('Status', {
#             'fields': ('owner', 'status')
#         }),
#     )

#     def has_add_permission(self, request):
#         return False


# @admin_site.register(Queue)
# class QueueAdmin(admin.ModelAdmin):
#     list_display = ('id', 'record', 'work_type', 'duration', 'owner', 'total_price', 'work_length', 'mistakes_length', 'locked', 'completed', 'checked', 'priority', 'skipped')
#     list_filter = ('priority', 'work_type', 'locked', 'completed', 'checked')

#     readonly_fields = ('total_price', 'work_length', 'mistakes_length', 'original_transcription', 'transcription', 'checked_transcription')

#     fieldsets = (
#         (None, {
#             'fields': ('order', 'piece', 'audio_file')
#         }),
#         ('Result', {
#             'fields': ('original_transcription', 'transcription', 'checked_transcription')
#         }),
#         ('Work and payment information', {
#             'fields': ('total_price', 'price', 'work_type', 'work_length', 'mistakes_length', 'priority')
#         }),
#         ('Worker', {
#             'classes': ('collapse',),
#             'fields': ('owner', 'locked', 'completed')
#         })
#     )

#     inlines = [TranscriptionInline]

#     def record(self, instance):
#         return instance.piece.record

#     def duration(self, instance):
#         return instance.end_at - instance.start_at

#     def total_price(self, instance):
#         queue_object_id = ContentType.objects.get_for_model(Queue).id

#         try:
#             payment = Payment.objects.get(content_type_id=queue_object_id, object_id=instance.id)

#             return payment.total
#         except:
#             return 0

#     def has_add_permission(self, request):
#         return False
