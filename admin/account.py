#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin import StackedInline
from django.db.models import Sum
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from work.models import Account, Order, Queue

from numpy import mean
from site import admin_site


class AccountInline(StackedInline):
    model = Account

    readonly_fields = ('transcribe_speed', 'check_speed')

    def speed(self, instance, work_type):
        durations = []
        time_spent = []
        speed = []

        for queue in instance.user.queue.\
                        filter(completed__isnull=False, work_type__exact=work_type):
            spent = (queue.completed - queue.locked).total_seconds()
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


class UserAdmin(UserAdmin):
    list_display = (
        'username',
        'balance',
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


# admin_site.unregister(User)
admin_site.register(User, UserAdmin)
