#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db import models

from django.contrib.contenttypes.models import ContentType

from django.conf import settings

from transcribe.models import *

from core.models import *

from account import Price

from pydub import AudioSegment


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
    record = models.ForeignKey(Record, related_name='orders')
    start_at = models.FloatField()
    end_at = models.FloatField()

    price = models.ForeignKey(Price)

    created = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey('auth.User', related_name='user_orders')

    def __unicode__(self):
        return "Record %d. %d-%d" % (self.record.id, self.start_at, self.end_at)

    def spent_money(self, work_type=0, owner_id=None):
        # Берём айдишники выполненной очереди
        object_id = ContentType.objects.get_for_model(Queue).id
        if owner_id:
            queue_ids = self.queue.filter(completed__isnull=False, work_type=work_type, owner_id=owner_id).values('id').distinct()
        else:
            queue_ids = self.queue.filter(completed__isnull=False, work_type=work_type).values('id').distinct()

        # по ним считаем сколько платежей
        return Payment.objects.filter(content_type_id=object_id, object_id__in=queue_ids).aggregate(total=Sum('total'))["total"]

    def completed_percentage(self, work_type=0):
        return (self.queue.filter(completed__isnull=False, work_type=work_type).count() / float(self.queue.filter(work_type=work_type).count())) * 100

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
                work_type=Price.WORK_TYPE_EDIT,
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

            queue.audio_file_make(as_record)

        # Загружаем mp3 файл записи
        mp3_file_path = settings.MEDIA_ROOT + \
            self.record.audio_file_format("mp3")

        # Загружаем эмпэтришку, черезе AudioSegment для нарезки
        record = AudioSegment.from_mp3(mp3_file_path)

        # Если очередь уже существует, то не даём создавать
        if self.queue.count() > 0:
            # print "Queue for Order already exist. \n Try to flush_queue before make a new."
            raise LookupError("Queue for Order already exist. \n Try to flush_queue before make a new.")

        pieces = self.record.pieces.all().order_by('start_at')

        for index, piece in enumerate(pieces):
            # Очередь на транскрибацию
            # Нечётные части приоритетные.
            # Для того, чтобы транскрибция начиналась с первого куска.
            priority = 0 if index % 2 else 1
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