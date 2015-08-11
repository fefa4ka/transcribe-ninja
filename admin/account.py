#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin import StackedInline, TabularInline, ModelAdmin
from django.db.models import Sum
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from work.models import Account, Order, Queue, Payment, Price

from django_mailbox.models import Message

from numpy import mean
from site import admin_site

import core.async_jobs


# def flush_work(modeladmin, request, queryset):
#     """
#         Режем на куски, если не порезано
#     """
#     for user in queryset.all():
#         core.async_jobs.flush_user_work.delay(user)


# class AccountInline(StackedInline):
#     model = Account

    # readonly_fields = ('transcribe_speed', 'check_speed')

    # def speed(self, instance, work_type):
    #     durations = []
    #     time_spent = []
    #     speed = []

    #     for queue in instance.user.queue.\
    #                     filter(completed__isnull=False, work_type__exact=work_type):
    #         spent = (queue.completed - queue.locked).total_seconds() or 1.0
    #         durations.append(queue.duration)
    #         time_spent.append(spent)

    #         if work_type == 0:
    #             length = len(queue.transcription)
    #             # Скорость знаков в минуту
    #             speed.append(length * 60 / spent)
    #         else:
    #             # Скорость измеряется в коээфициенте
    #             # на которое умнажается время записи
    #             speed.append(spent / queue.duration)

    #     return mean(speed)

    # def transcribe_speed(self, instance):
    #     return self.speed(instance, 0)

    # def check_speed(self, instance):
    #     return self.speed(instance, 1)


# class PaymentClientInline(TabularInline):
#     # TODO DONT WORK!!!!
#     model = Payment

#     extra = 1
#     # exclude = ("user", ) # auto-update user field in save_formset method of parent modeladmin.
#     def __init__(self, model, admin_site, dist=False):
#         self.dist = dist
#         super(PaymentClientInline, self).__init__(model, admin_site)

#     def formfield_for_foreignkey(self, field, request, **kwargs):
#         parent_user = self.get_object(request, User)
#         queue_object_id = ContentType.objects.get_for_model(Queue).id
#         print "EBALA"
#         kwargs["queryset"] = Payment.objects.filter(owner=parent_user).exclude(content_type_id=queue_object_id)

#         return super(PaymentClientInline, self).formfield_for_foreignkey(field, request, **kwargs)

#     def get_object(self, request, model):
#         object_id = request.META['PATH_INFO'].strip('/').split('/')[-1]
#         return model.objects.get(pk=object_id)


# class MessageInline(StackedInline):
#     model = Message

#     def queryset(self, request):
#         print request
#         qs = Message.objects.filter(from_header__icontains=db_field.email)

#         return qs

class AccountAbstractAdmin(ModelAdmin):
    class Meta:
        abstract = True
        model = Account
        js = ('js/admin/account.js',)
        css = {
             'all': ('css/admin/account.css',)
        }

    readonly_fields = ('username', 'email',)

    fieldsets = (
        (None, {
            'fields': ('username', 'email', 'phone',)
        }),
    )

    def username(self, instance):
        if instance.user.first_name or instance.user.last_name:
            return " ".join([instance.user.first_name, instance.user.last_name])
        else:
            return instance.user.username
    username.admin_order_field  = 'user__username'  #Allows column order sorting
    username.short_description = 'Name'  #Renames column head

    def email(self, instance):
        return instance.user.email
    email.admin_order_field  = 'user__email'  #Allows column order sorting
    email.short_description = 'Email'  #Renames column head


if settings.DOMAIN == "stenograph.us":
    class AccountAdmin(AccountAbstractAdmin):
        # class Meta:
        #     model = Account
        list_display = ('username', 'balance', 'records', 'spent_money')


        def records(self, instance):
            return instance.user.records.count()
        # records.admin_order_field  = 'user__records'  #Allows column order sorting
        records.short_description = 'Records'  #Renames column head

        def spent_money(self, instance):
            order_type_id = ContentType.objects.get_for_model(Order).id
            payments = instance.user.payments.filter(price__work_type=Price.WORK_TYPE_TRANSCRIBE).aggregate(total=Sum('total'))

            return payments['total'] or 0
        spent_money.short_description = 'Spent Money'  #Renames column head

else:
    class AccountAdmin(AccountAbstractAdmin):
        # class Meta:
        #     model = Account
        list_display = ('username', 'actual_rating', 'balance', 'checked_balance')
        readonly_fields = ('actual_rating', 'work_length', 'mistakes_part', 'empty_part', 'tc_index',)
        
        fieldsets = (
            ('Rating', {
                'classes': ('collapse',),
                'fields': ('actual_rating', 'work_length', 'mistakes_part', 'empty_part', 'tc_index',)
            }),
            ('Language', {
                'classes': ('collapse',),
                'fields': ('languages',)
            }),
        )
        def get_queryset(self, request):
            qs = super(AccountAdmin, self).get_queryset(request)

            return qs.filter(site=settings.DOMAIN)


class UserAdmin(UserAdmin):
    list_display = (
        'username',
        'balance',
        'checked_balance',
        'work_length',
        'mistakes_part',
        'transcribe_count',
        'check_count'
    )
    list_filter = (
        'account__blind',
        'last_login',
        'date_joined'
    )

    # inlines = (AccountInline)

    def balance(self, instance):
        return instance.account.balance

    def checked_balance(self, instance):
        return instance.account.checked_balance
        
    # def balance(self, instance):
    #     queue_object_id = ContentType.objects.get_for_model(Queue).id
    #     order_object_id = ContentType.objects.get_for_model(Order).id
    #     account_object_id = ContentType.objects.get_for_model(Account).id

    #     if settings.DOMAIN == "transcribe.ninja":
    #         object_ids = [queue_object_id, account_object_id]
    #     else:
    #         object_ids = [order_object_id, account_object_id]

    #     for balance in instance.account.balances:
    #         if balance['content_type_id'] in object_ids:
    #             return balance["total"] or 0

    #     return 0

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


# admin_site.unregister(User)
admin_site.register(Account, AccountAdmin)
