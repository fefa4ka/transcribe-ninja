#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin import StackedInline, TabularInline
from django.db.models import Sum
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from work.models import Account, Order, Queue, Payment

from numpy import mean
from site import admin_site

import core.async_jobs


def flush_work(modeladmin, request, queryset):
    """
        Режем на куски, если не порезано
    """
    for user in queryset.all():
        core.async_jobs.flush_user_work.delay(user)


class AccountInline(StackedInline):
    model = Account

    readonly_fields = ('transcribe_speed', 'check_speed')

    actions = [flush_work]

    def speed(self, instance, work_type):
        durations = []
        time_spent = []
        speed = []

        for queue in instance.user.queue.\
                        filter(completed__isnull=False, work_type__exact=work_type):
            spent = (queue.completed - queue.locked).total_seconds() or 1.0
            durations.append(queue.duration)
            time_spent.append(spent)

            if work_type == 0:
                length = len(queue.transcription)
                # Скорость знаков в минуту
                speed.append(length * 60 / spent)
            else:
                # Скорость измеряется в коээфициенте
                # на которое умнажается время записи
                speed.append(spent / queue.duration)

        return mean(speed)

    def transcribe_speed(self, instance):
        return self.speed(instance, 0)

    def check_speed(self, instance):
        return self.speed(instance, 1)


class PaymentClientInline(TabularInline):
    # TODO DONT WORK!!!!
    model = Payment

    extra = 1
    # exclude = ("user", ) # auto-update user field in save_formset method of parent modeladmin.
    def __init__(self, model, admin_site, dist=False):
        self.dist = dist
        super(PaymentClientInline, self).__init__(model, admin_site)

    def formfield_for_foreignkey(self, field, request, **kwargs):
        parent_user = self.get_object(request, User)
        queue_object_id = ContentType.objects.get_for_model(Queue).id
        print "EBALA"
        kwargs["queryset"] = Payment.objects.filter(owner=parent_user).exclude(content_type_id=queue_object_id)

        return super(PaymentClientInline, self).formfield_for_foreignkey(field, request, **kwargs)

    def get_object(self, request, model):
        object_id = request.META['PATH_INFO'].strip('/').split('/')[-1]
        return model.objects.get(pk=object_id)



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

    inlines = (AccountInline,)

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
admin_site.register(User, UserAdmin)
