#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db import models

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
import django.db.models.signals as signals

from transcribe.models import *

import os


class Price(models.Model):
    content_type = models.ForeignKey(ContentType)

    title = models.CharField(max_length=255)
    work_type = models.IntegerField(default=0)
    price = models.FloatField()

    default = models.BooleanField(default=False)

    def __unicode__(self):
        return self.title


class Order(models.Model):
    record = models.ForeignKey(Record)
    start_at = models.FloatField()
    end_at = models.FloatField()

    price = models.ForeignKey(Price)

    owner = models.ForeignKey('auth.User', related_name='user-orders')

    trashed_at = models.DateTimeField(blank=True, null=True)

    objects = NonTrashManager()
    trash = TrashManager()

    def delete(self, trash=True):
        if not self.trashed_at and trash:
            self.trashed_at = datetime.now()
            self.save()
        else:
            super(Order, self).delete()

    def restore(self, commit=True):
        self.trashed_at = None
        if commit:
            self.save()


class Queue(models.Model):
    order = models.ForeignKey(Order)
    piece = models.ForeignKey(Piece)
    file_name = models.FileField(
        max_length=255,
        upload_to=upload_queue_path
    )
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

    owner = models.ForeignKey('auth.User', null=True)
    priority = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    locked = models.BooleanField(default=False)
    locked_time = models.DateTimeField(null=True)

    def start_at(self):
        return np.round(self.piece.start_at)

    def end_at(self):
        if self.work_type == 0:
            return np.round(self.piece.end_at)
        else:
            next_piece = Piece.objects.filter(
                start_at__gte=self.piece.end_at).order_by('start_at')[0]
            return np.round(
                next_piece.end_at
            )


class Payment(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    price = models.ForeignKey(Price)
    total = models.FloatField()
    status = models.IntegerField(default=0)

    owner = models.ForeignKey('auth.User', related_name='user-payments')
    time = models.DateTimeField(auto_now=True)


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
