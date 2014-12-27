#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db import models

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
import django.db.models.signals as signals

from transcribe.models import *

from core.models import *

import os


class Price(models.Model):
    """
        Цена за разные работы.
        Цена определяется: типом данных, типом работ.

        Тип данных: Order, Piece, Transcription и любой другой
        title       - название
        work_type   - тип работы, пока не понятно зачем,
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

    WORK_TYPE_TRANCRIBE = 0
    WORK_TYPE_CHECK = 1
    WORK_TYPE_EDIT = 2
    WORK_TYPE_CHOICES = (
        (WORK_TYPE_TRANCRIBE, 'Transcribe audio piece'),
        (WORK_TYPE_CHECK, 'Read and check transcription'),
        (WORK_TYPE_EDIT, 'Transcription edit')
    )
    work_type = models.IntegerField(
        choices=WORK_TYPE_CHOICES,
        default=WORK_TYPE_TRANCRIBE
    )
    price = models.FloatField()

    default = models.BooleanField(default=False)

    def __unicode__(self):
        return self.title


class Order(Trash):
    """
        Зазаз на стенографирование
        record      - стенографируемая запись
        start_at    - начинать с секунды
        end_at      - заканчивать с секунды

        price       - по какой цене стенографируется

        created     - когда был сделан заказ
        owner       - заказчик стенографирования

    """
    record = models.ForeignKey(Record)
    start_at = models.FloatField()
    end_at = models.FloatField()

    price = models.ForeignKey(Price)

    created = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey('auth.User', related_name='user-orders')

    # Logic
    def make_queue(self):
        """
            Создаём очередь на распознание
        """
        mp3_file_path = self.record.save_to_file(path=settings.TEMP_DIR)

        # Загружаем эмпэтришку, черезе AudioSegment для нарезки
        record = AudioSegment.from_mp3(mp3_file_path)

    def make_transcribe_queue(self):
        pass

    def make_check_queue(self):
        pass


class Queue(AudioFile):
    """
        Элемент очереди, для стенографирования.
        Каждый элемент содержит информацию о работе,
        нужной для стенографирования задписи.

        Работа может быть:
        1. Стенографирование
        2. Проверка транскрибции

        Работа связана с каким-то куском записи, если стенографируется.
        И с двумя кусками рядом, если проверяется.

        order       - заказ, с которым связана работа
        piece       - кусок, для которого делается работа

        audio_file  - аудиозапись, связанная с этим куском

        price       - прайс, по которому должна быть сделана работа

        work_type   - тип работы: стенографирование TRANSCRIBE
                      или проверка CHECK

        priority    - булевый приоритет
                      False - не приоритетно
                      True - приоритетно

        locked      - время, когда эту задачу отдали на выполнение

        owner       - кому отдали задачу, или кто её выполнил

        completed   - время, когда задача была выполнена

    """
    order = models.ForeignKey(Order)
    piece = models.ForeignKey(Piece)

    price = models.ForeignKey(Price)

    TRANSCRIBE = 0
    CHECK = 1
    WORK_TYPE_CHOICES = (
        (TRANSCRIBE, 0),
        (CHECK, 1)
    )
    work_type = models.IntegerField(
        choices=WORK_TYPE_CHOICES,
        default=TRANSCRIBE
    )

    priority = models.BooleanField(default=False)

    locked = models.DateTimeField(null=True)

    owner = models.ForeignKey('auth.User', null=True)
    completed = models.DateTimeField(null=True)

    def start_at(self):
        """
            Начала куска относительно всей записи
        """
        return np.round(self.piece.start_at)

    def end_at(self):
        """
            Конец куска относительно всей записи
        """
        # Если очередь на стенографирование,
        # то просто берём время окончания у связанного куска
        if self.work_type == self.TRANSCRIBE:
            return np.round(self.piece.end_at)

        # Если проверка, то провремя кусок в связке с соседним.
        elif self.work_type == self.CHECK:
            # Берём время, когда заканчивается кусок, следующий за текущим.
            next_piece = Piece.objects.filter(
                start_at__gte=self.piece.end_at).order_by('start_at')[0]

            # TODO: Если следующего нет, то ничего не делаем.
            return np.round(
                next_piece.end_at
            )


class Payment(models.Model):
    """
        История платежей.
        Платежи привязаны к конкретному объекту в базе:
            Order, Piece, Transcription и другие

        content_object  - объект, с которым связан платёж

        price           - прайс, по которому считался платёж
        total           - размер платежа

        status          - статус платежа с внешним миром. Наверное, проведёт или не проведёт.
                          Видно будет, когда платёжную систему подключим.

        created         - дата проведения платежа
        owner           - с кем связан платёж
    """
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    price = models.ForeignKey(Price)
    total = models.FloatField()

    status = models.IntegerField(default=0)

    created = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey('auth.User', related_name='user-payments')


def create_order_payment(sender, instance, **kwargs):
    # Берём дефолтный прайс для объекта

    owner = instance.owner

    object_id = ContentType.objects.get_for_model(type(instance)).id
    price = Price.objects.filter(content_type_id=object_id, default=1)[0]
    duration = instance.end_at - instance.start_at
    total = price.price * duration / 60

    payment = Payment(
        content_object=instance,
        price=price,
        total=total,
        owner=owner)

    owner.account.balance -= total

    payment.save()
    owner.account.save()

    instance.record.progress = 1
    instance.record.save()


def create_queue_payment(sender, instance, **kwargs):
    # Берём дефолтный прайс для объекта

    if not instance.completed:
        return

    owner = instance.owner

    price = instance.price

    total = 0

    payment = Payment(
        content_object=instance,
        price=price,
        total=total,
        owner=owner)

    owner.account.balance += total

    payment.save()
    owner.account.save()

# register the signal
signals.post_save.connect(create_order_payment, sender=Order)
signals.post_save.connect(create_queue_payment, sender=Queue)
