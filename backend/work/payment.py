#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
import django.db.models.signals as signals
from django.conf import settings

from price import Price

from dbmail import send_db_mail


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

    comment = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    status = models.BooleanField(default=0)

    created = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey('auth.User', related_name='payments')

    def __unicode__(self):
        return "Payment for %s: %s" % (self.content_object.__class__.__name__, self.content_object)


def send_mail(sender, instance, **kwargs):
    # Берём дефолтный прайс для объекта
    if not instance.id:
        return

    payment = Payment.objects.get(id=instance.id)

    if payment.status == 0 and instance.status == 1 and settings.DOMAIN == 'transcribe.ninja':
        if payment.owner.email:
            send_db_mail('ninja-payment-success', payment.owner.email, { 'name': payment.owner.first_name, 'total': payment.total * -1 })

# register the signal
signals.pre_save.connect(send_mail, sender=Payment)
