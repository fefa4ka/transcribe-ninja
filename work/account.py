#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from django.db import models
from django.db.models import Sum

import django.db.models.signals as signals

from django.conf import settings


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

    rating = models.FloatField(default=0)
    balance = models.FloatField(default=0)
    site = models.CharField(max_length=50)

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
    def balances(self):
        """
            Балансы по разным типам платежей
        """
        balances = self.user.user_payments.values('content_type_id').annotate(total=Sum('total'))

        return balances

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


class Price(models.Model):

    """
        Цена за разные работы.
        Цена определяется: типом данных, типом работ.

        Тип данных: Order, Piece, Transcription и любой другой
        title       - название
        work_type   - тип работы,
                      возможно, сделать единицу измерения: мин, символ, штуки

        price       - цена. В основном это цена за единицу чего-то.
                      За минуту разспознавание, за символ в транскрибции,
                      за исправленный символ, за прослушку записи

        default     - возможно, будут плавающие цены,
                      для разных пользователей.
                      Пока везде выбираются цены по умолчанию

    """
    # Цена определяется: типом данных, типом работы
    content_type = models.ForeignKey(ContentType)

    title = models.CharField(max_length=255)
    work_type = models.IntegerField(default=0)

    WORK_TYPE_TRANSCRIBE = 0
    WORK_TYPE_EDIT = 1
    WORK_TYPE_LISTENING = 2
    WORK_TYPE_TRANSCRIBE_SPEECHKIT = 3
    WORK_TYPE_CHOICES = (
        (WORK_TYPE_TRANSCRIBE, 'Transcribe audio piece'),
        (WORK_TYPE_LISTENING, 'Read and check transcription'),
        (WORK_TYPE_EDIT, 'Transcription edit'),
        (WORK_TYPE_TRANSCRIBE_SPEECHKIT, 'Transcribe by SpeechKit')
    )
    work_type = models.IntegerField(
        choices=WORK_TYPE_CHOICES,
        default=WORK_TYPE_TRANSCRIBE
    )

    price = models.FloatField()

    default = models.BooleanField(default=False)

    def __unicode__(self):
        return self.title


def create_account(sender, instance, **kwargs):
    """
        Создание учётки, если она не создана
    """
    try:
        instance.account
        pass
    except:
        instance.account = Account(site=settings.DOMAIN)
        instance.account.save()


# После сохранении User, создаём Account, если ещё не создан
signals.post_save.connect(create_account, sender=User)
