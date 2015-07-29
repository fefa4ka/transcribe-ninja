#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import Sum
import django.db.models.signals as signals
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from core.models import Trash
from transcribe.models import Record

from price import Price
from payment import Payment

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

    editing = models.BooleanField()
    speedup = models.BooleanField()

    price = models.ForeignKey(Price)

    created = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey('auth.User', related_name='user_orders')

    def __unicode__(self):
        return "Record %d. %d-%d" % (self.record.id, self.start_at, self.end_at)

    def spent_money(self, work_type=0, owner_id=None):
        if self.queue.filter(completed__isnull=False).count() == 0:
            return 0

        # Берём айдишники выполненной очереди
        object_id = ContentType.objects.get_for_model(self.queue.all()[0]).id
        if owner_id:
            queue_ids = self.queue.filter(completed__isnull=False, work_type=work_type, owner_id=owner_id).values('id').distinct()
        else:
            queue_ids = self.queue.filter(completed__isnull=False, work_type=work_type).values('id').distinct()

        # по ним считаем сколько платежей
        return Payment.objects.filter(content_type_id=object_id, object_id__in=queue_ids).aggregate(total=Sum('total'))["total"]

    def completed_percentage(self, work_type=0):
        total_queue_count = self.queue.filter(work_type=work_type).count()

        if total_queue_count:
            return (self.queue.filter(completed__isnull=False, work_type=work_type).count() / float(total_queue_count)) * 100
        else:
            return 0

    # Logic
    def make_queue(self):
        """
            Создаём очередь на распознание
        """

        from queue import Queue

        def make_queue_element(order, piece, work_type, price, priority):
            try:
                Queue.get(order=self,
                          piece=piece,
                          price=price,
                          work_type=work_type)
            except:
                queue = Queue(order=self,
                          piece=piece,
                          price=price,
                          work_type=work_type,
                          priority=priority)

                queue.save()

                queue.audio_file_make()

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

        # Загружаем mp3 файл записи
        mp3_file_path = settings.MEDIA_ROOT + \
            self.record.audio_file_format("mp3")

        pieces = self.record.pieces.all().order_by('start_at')

        for index, piece in enumerate(pieces):
            # Если очередь уже существует, то не даём создавать
            if piece.queue.count() == 2:
                continue

            # Очередь на транскрибацию
            # Нечётные части приоритетные.
            # Для того, чтобы транскрибция начиналась с первого куска.
            priority = 0 if index % 2 else 1

            make_queue_element(self,
                               piece=piece,
                               work_type=0,
                               price=transcribe_price,
                               priority=priority)

            # Очередь на вычитку
            make_queue_element(self,
                               piece=piece,
                               work_type=1,
                               price=check_price,
                               priority=False)

    def flush_queue(self):
        self.queue.all().delete()


def create_order_payment(sender, instance, created, **kwargs):
    if not created:
        return

    owner = instance.owner

    object_id = ContentType.objects.get_for_model(type(instance)).id
    transcribe_price = Price.objects.\
        get(content_type_id=object_id, work_type=Price.WORK_TYPE_TRANSCRIBE, default=1)
    editing_price = Price.objects.\
        get(content_type_id=object_id, work_type=Price.WORK_TYPE_EDITING, default=1)
    speedup_price = Price.objects.\
        get(content_type_id=object_id, work_type=Price.WORK_TYPE_SPEEDUP, default=1)

    duration = instance.end_at - instance.start_at
    total = (transcribe_price.price + instance.speedup * speedup_price.price + instance.editing * editing_price.price) * duration / 60

    payment = Payment(
        content_object=instance,
        price=transcribe_price,
        total=total,
        owner=owner)

    payment.save()
    owner.account.save()

    instance.record.progress = 1
    instance.record.save()


signals.post_save.connect(create_order_payment, sender=Order)
