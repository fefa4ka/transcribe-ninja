#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from django.db import models
from django.db.models import Sum

import django.db.models.signals as signals

from django.conf import settings

from django_mailbox.models import Message

from price import Price

from core.models import Language


class Account(models.Model):
    """
        Расширенная информация по учётной записи

    properties:
        user    - пользователь

        phone   - номер телефона

        rating   - рейтинг

        balance - баланс

        site    - источник регистрации

        work_length — количество набранных символов, минус ошибки

        balances - балансы по разным типам платежей

        avg_speed - средняя скорость набора

    methods:
        calculate_work(unchecked, after_date) - возвращает
            (work_length, mistakes_lenght) по статусу очереди и дате

        queues(uncheced, after_date) - список очередей

    """

    user = models.OneToOneField(User)

    phone = models.CharField(max_length=50, blank=True, null=True)

    blind = models.BooleanField(default=0)
    rating = models.FloatField(default=0)
    site = models.CharField(max_length=50)

    price = models.ForeignKey(Price)

    languages = models.ManyToManyField(Language)

    def __unicode__(self):
        return "%d: %s" % (self.id, self.user.username)

    @property
    def work_length(self):
        """
            Количество набранных символов, минус ошибки (всего)
        """
        try:
            work = self.user.queue.all().aggregate(work=Sum('work_length'))
            mistakes = self.user.queue.all().aggregate(mistakes=Sum('mistakes_length'))

            return work['work'] - mistakes['mistakes']
        except:
            # Если не работал. Вылетает ошибка, потому что не нашлись записи
            return 0

    @property
    def mistakes_part(self):
        mistakes_length = self.user.queue.all().aggregate(lenght=Sum('mistakes_length'))["lenght"] or 0
        work_length = self.work_length

        if work_length > 0:
            mistakes_part = round(mistakes_length / float(work_length), 2)
        else:
            mistakes_part = 0

        return mistakes_part

    @property
    def check_mistakes_part(self):
        empty_count = self.user.queue.filter(work_type=Price.WORK_TYPE_EDIT, work_length__gt=0, mistakes_length__gt=0).count()
        check_count = self.user.queue.filter(work_type=Price.WORK_TYPE_EDIT).count()

        if check_count > 0:
            empty_part = round(empty_count / float(check_count), 2)
        else:
            empty_part = 0

        return empty_part

    @property
    def empty_part(self):
        empty_count = self.user.queue.filter(work_type=Price.WORK_TYPE_EDIT, work_length=0, mistakes_length__gt=0).count()
        check_count = self.user.queue.filter(work_type=Price.WORK_TYPE_EDIT).count()

        if check_count > 0:
            empty_part = round(empty_count / float(check_count), 2)
        else:
            empty_part = 0

        return empty_part

    @property
    def tc_index(self):
        transcribe_count = self.user.queue.filter(work_type=Price.WORK_TYPE_TRANSCRIBE).count()
        check_count = self.user.queue.filter(work_type=Price.WORK_TYPE_EDIT).count()

        if check_count > 0:
            empty_part = round(transcribe_count / float(check_count), 2)
        else:
            empty_part = 0

        return empty_part

    @property
    def actual_rating(self):
        if self.empty_part == 0:
            queue_rating = 1
        else:
            queue_rating = self.empty_part / 0.05

        if self.mistakes_part == 0:
            mistakes_rating = 1
        else:
            mistakes_rating = self.mistakes_part / 0.05

        return round(2 / (queue_rating + mistakes_rating), 2)

    @property
    def balance(self):
        from .models import Queue, Order

        queue_object_id = ContentType.objects.get_for_model(Queue).id
        order_object_id = ContentType.objects.get_for_model(Order).id
        account_object_id = ContentType.objects.get_for_model(Account).id

        user_balance = 0

        if settings.DOMAIN == "transcribe.ninja":
            object_ids = [queue_object_id, account_object_id]
        else:
            object_ids = [order_object_id, account_object_id]

        for balance in self.balances:
            if balance['content_type_id'] in object_ids:
                if balance['content_type_id'] == order_object_id:
                    user_balance -= balance["total"] or 0
                else:
                    user_balance += balance["total"] or 0

        return user_balance

    @property
    def balances(self):
        """
            Балансы по разным типам платежей
        """
        balances = self.user.payments.values('content_type_id').annotate(total=Sum('total'))

        return balances

    @property
    def actual_price(self):
        """
            Актуальная цена
        """
        from .models import Queue, Order

        queue_type_id = ContentType.objects.get_for_model(Queue).id
        order_type_id = ContentType.objects.get_for_model(Order).id

        # Аккаунты одни для всех, а прайс один на аккаунт
        # поэтому если прайс не на тот тип объекта стоит, выдаём прайс дефолтный
        if settings.DOMAIN == "transcribe.ninja":
            type_id = queue_type_id
        else:
            type_id = order_type_id

        if not self.price or self.price.content_type_id != type_id:
            price = Price.objects.filter(content_type_id=type_id, default=1)[0]

            return price
        else:
            return self.price

    @property
    def emails(self):
        return Message.objects.filter(from_header__icontains=self.user.email).order_by('-processed')

    @property
    def checked_balance(self):
        from .models import Queue
        account_object_id = ContentType.objects.get_for_model(Account).id
        queue_object_id = ContentType.objects.get_for_model(Queue).id

        balance = self.user.payments.filter(content_type_id=account_object_id).aggregate(total=Sum('total'))

        checked_ids = self.queues(unchecked=False).values('id').distinct()
        checked_total = self.user.payments.filter(content_type_id=queue_object_id, object_id__in=checked_ids).aggregate(total=Sum('total'))

        return (checked_total['total'] or 0) + (balance['total'] or 0)

    def calculate_work(self, unchecked=False, after_date=None):
        """
            Возвращает
            (work_length, mistakes_lenght) по статусу очереди и дате

            unchecked - True выдаёт статистику по непроверенным записям.
                По умолчанию False

            after_date - дата, начиная с которой считать
        """
        try:
            work = self.queues(unchecked=unchecked, after_date=after_date).aggregate(work=Sum('work_length'))
            mistakes = self.queues(unchecked=unchecked, after_date=after_date).aggregate(mistakes=Sum('mistakes_length'))

            return (work['work'], mistakes['mistakes'])
        except:
            return 0

    def queues(self, unchecked=False, after_date=None):
        """
            Список очередей пользователя

            unchecked - True выдаёт список по непроверенным записям.
                По умолчанию False

            after_date - дата, начиная с которой смотреть
        """
        if not after_date:
            return self.user.queue.filter(completed__isnull=False, checked__isnull=unchecked)
        else:
            return self.user.queue.filter(completed__isnull=False, checked__isnull=unchecked, completed__gt=after_date)


def post_account_save(sender, instance, **kwargs):
    """
        Создание учётки, если она не создана
    """
    from .models import Queue, Order
    try:
        instance.account
        pass
    except:
        queue_type_id = ContentType.objects.get_for_model(Queue).id
        order_type_id = ContentType.objects.get_for_model(Order).id
        # Аккаунты одни для всех, а прайс один на аккаунт
        # поэтому если прайс не на тот тип объекта стоит, выдаём прайс дефолтный
        if settings.DOMAIN == "transcribe.ninja":
            type_id = queue_type_id
        else:
            type_id = order_type_id

        transcribe_price = Price.objects.get(content_type_id=type_id, work_type=Price.WORK_TYPE_TRANSCRIBE, default=1)

        instance.account = Account(site=settings.DOMAIN, price=transcribe_price)
        instance.account.save()

        # Сделать языки, которые указал
        ru = Language.objects.get(code='RU')
        # de = Language.objects.get(code='DE')
        instance.account.languages.add(ru)


# def pre_user_save(sender, instance, *args, **kwargs):
    # pass
    # if instance.active != User.objects.get(id=instance.id).active:
        # TO DO: Слать сообщение
        # send_mail(
        #     subject='Active changed: %s -> %s' % (instance.username, instance.active),
        #     message='Guess who changed active status??',
        #     from_email=settings.SERVER_EMAIL,
        #     recipient_list=[p[1] for p in settings.MANAGERS],
        # )

# signals.pre_save.connect(pre_user_save, sender=User, dispatch_uid='pre_user_save')

# После сохранении User, создаём Account, если ещё не создан
signals.post_save.connect(post_account_save, sender=User)
