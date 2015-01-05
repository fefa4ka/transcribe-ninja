#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db import models

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
import django.db.models.signals as signals

from transcribe.models import *

from core.models import *

import os

from pydub import AudioSegment


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

    WORK_TYPE_TRANSCRIBE = 0
    WORK_TYPE_CHECK = 1
    WORK_TYPE_EDIT = 2
    WORK_TYPE_CHOICES = (
        (WORK_TYPE_TRANSCRIBE, 'Transcribe audio piece'),
        (WORK_TYPE_CHECK, 'Read and check transcription'),
        (WORK_TYPE_EDIT, 'Transcription edit')
    )
    work_type = models.IntegerField(
        choices=WORK_TYPE_CHOICES,
        default=WORK_TYPE_TRANSCRIBE
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

    def __unicode__(self):
        return "Record %d. %d-%d" % (self.record.id, self.start_at, self.end_at)

    # Logic
    def make_queue(self):
        """
            Создаём очередь на распознание
        """
        def make_queue_element(order, as_record, piece, work_type, priority):
            transcribe_object_id = ContentType.objects.get_for_model(Queue).id
            transcribe_price = Price.objects.filter(
                content_type_id=transcribe_object_id,
                work_type=Price.WORK_TYPE_TRANSCRIBE,
                default=1)[0]

            check_object_id = ContentType.objects.get_for_model(Queue).id
            check_price = Price.objects.filter(
                content_type_id=check_object_id,
                work_type=Price.WORK_TYPE_CHECK,
                default=1)[0]

            # work_type = 0 - транскрибция
            # work_type = 1 - вычитка
            price = transcribe_price if not work_type else check_price

            queue = Queue(order=self,
                          piece=piece,
                          price=price,
                          work_type=work_type,
                          priority=priority)

            queue.save()

            queue.audio_file_make(as_record=as_record)

        # Загружаем mp3 файл записи
        mp3_file_path = settings.MEDIA_ROOT + \
            self.record.audio_file_format("mp3")

        # Загружаем эмпэтришку, черезе AudioSegment для нарезки
        record = AudioSegment.from_mp3(mp3_file_path)

        # Если очередь уже существует, то не даём создавать
        if self.queue.count() > 0:
            print "Queue for Order already exist. \n Try to flush_queue before make a new."
            raise

        pieces = self.record.pieces.all().order_by('start_at')

        for index, piece in enumerate(pieces):
            # Очередь на транскрибацию
            # Нечётные части приоритетные.
            # Для того, чтобы транскрибция начиналась с первого куска.
            priority = False if index % 2 else True
            make_queue_element(self,
                               as_record=record,
                               piece=piece,
                               work_type=0,
                               priority=priority)

            # Очередь на вычитку
            make_queue_element(self,
                               as_record=record,
                               piece=piece,
                               work_type=1,
                               priority=False)

    def flush_queue(self):
        self.queue.all().delete()


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
    order = models.ForeignKey(Order, related_name='queue')

    piece = models.ForeignKey(Piece, related_name='queue')

    def set_pieces(self, val):
        self.piece = val

    def get_pieces(self):
        if self.work_type == self.CHECK:
            return [self.piece, self.piece.next()]
        else:
            return [self.piece]

    pieces = property(get_pieces, set_pieces)

    audio_file = models.FileField(
        max_length=255,
        upload_to=upload_queue_path)

    price = models.ForeignKey(Price)

    TRANSCRIBE = 0
    CHECK = 1
    WORK_TYPE_CHOICES = (
        (TRANSCRIBE, 'Transcribe'),
        (CHECK, 'Check and edit')
    )
    work_type = models.IntegerField(
        choices=WORK_TYPE_CHOICES,
        default=TRANSCRIBE
    )

    priority = models.BooleanField(default=False)

    locked = models.DateTimeField(null=True)
    skipped = models.IntegerField(default=0)

    owner = models.ForeignKey('auth.User',
                              blank=True,
                              null=True,
                              related_name='queue')
    completed = models.DateTimeField(null=True)




    def __unicode__(self):
        return "%d: %d-%d sec" % (self.id, self.start_at(), self.end_at())

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
            next_piece = self.piece.next()

            # TODO: Если следующего нет, то ничего не делаем.
            if not next_piece:
                return self.piece.end_at

            return np.round(
                next_piece.end_at
            )

    def audio_file_make(self, as_record=None, offset=1.5):
        """
            Создаёт вырезанный кусок в mp3

            rec - можно передать AudioSegment записи, чтобы ускорить процесс
            offset  - сколько записи по краям оставлять
        """
        # Если запись уже создана, возвращаем название файла
        if self.audio_file:
            return self.audio_file_local()

        # Если as_record не передали
        if not as_record:
            as_record = AudioSegment.from_mp3(
                settings.MEDIA_ROOT +
                self.piece.record.audio_file_format("mp3")
            )

        # Папка записи
        audio_file_path = os.path.join(
            str(self.piece.record.id),
            upload_queue_path(self)
        )

        audio_dir_path = os.path.dirname(settings.MEDIA_ROOT + audio_file_path)

        if not os.path.isfile(settings.MEDIA_ROOT + audio_dir_path):
            # Создаём папку, если её не было
            if not os.path.exists(audio_dir_path):
                os.makedirs(audio_dir_path)

            # В первой записи делаем отступ максмум до 0
            if self.start_at() > offset:
                start_at = (self.start_at() - offset) * 1000
            else:
                start_at = 0

            # В последней не больше, чем длинна записи
            if self.piece.record.duration > self.end_at() + offset:
                end_at = self.end_at() * 1000
            else:
                end_at = (self.end_at() + offset) * 1000

            # Вырезаем кусок и сохраняем
            piece = as_record[start_at:end_at]
            piece.export(settings.MEDIA_ROOT + audio_file_path)

            # Сохраняем на Амазон с3
            self.audio_file.delete()
            self.audio_file.save(
                audio_file_path,
                File(
                    open(settings.MEDIA_ROOT + audio_file_path)
                )
            )

            return audio_file_path


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


def create_order_payment(sender, instance, created, **kwargs):
    if not created:
        return

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


def create_queue_payment(sender, instance, created, **kwargs):
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
