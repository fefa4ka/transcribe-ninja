#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib.contenttypes.models import ContentType

from django.db import models


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
    WORK_TYPE_PAYMENT = 4
    WORK_TYPE_EDITING = 5
    WORK_TYPE_SPEEDUP = 6
    WORK_TYPE_CHOICES = (
        (WORK_TYPE_TRANSCRIBE, 'Transcribe audio piece'),
        (WORK_TYPE_LISTENING, 'Read and check transcription'),
        (WORK_TYPE_EDIT, 'Transcription edit'),
        (WORK_TYPE_TRANSCRIBE_SPEECHKIT, 'Transcribe by SpeechKit'),
        (WORK_TYPE_PAYMENT, 'Payment'),
    )
    work_type = models.IntegerField(
        choices=WORK_TYPE_CHOICES,
        default=WORK_TYPE_TRANSCRIBE
    )

    price = models.FloatField()

    default = models.BooleanField(default=False)

    def __unicode__(self):
        return self.title