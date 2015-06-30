#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db import models

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
import django.db.models.signals as signals

from transcribe.models import *

from core.models import *

from account import Price

from order import Order

from queue import Queue

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
    owner = models.ForeignKey('auth.User', related_name='user_payments')


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


def create_queue_payment(sender, instance, created, raw, using, update_fields, **kwargs):
    # Берём дефолтный прайс для объекта
    if not instance.completed:
        return

    # Если есть платёж, новый не создаём
    try:
        type_id = ContentType.objects.get_for_model(type(instance)).id
        payment = Payment.objects.get(content_type_id=type_id, object_id=instance.id)
        return
    except Payment.DoesNotExist:
        pass

    # TODO: Если платёж по этому объекту уже есть, то ничего не делать

    owner = instance.owner

    price = instance.price

    total = instance.total_price

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