#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db import models

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from backend.transcribe.models import *

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
            super(SomeModel, self).delete()

    def restore(self, commit=True):
        self.trashed_at = None
        if commit:
            self.save()

class Queue(models.Model):
    piece = models.ForeignKey(Piece)
    price = models.ForeignKey(Price)
    work_type = models.IntegerField()

    except_user = models.ForeignKey('auth.User', null=True)
    locked = models.BooleanField(default=False)
    locked_time = models.DateTimeField(null=True)

    def make_mp3(self, offset=1.5):
        if not os.path.isfile(settings.RECORD_ROOT + self.mp3_path()):
            rec = AudioSegment.from_mp3(
                settings.RECORD_ROOT + self.piece.record.file_name_format('mp3'))
            piece = rec[
                np.round((self.peice.start_at - offset) * 1000):
                np.ceil((self.piece.end_at + offset) * 1000)
            ]
            piece.export(settings.RECORD_ROOT + self.mp3_path())

    def remove_mp3(self):
        os.remove(settings.RECORD_ROOT + self.mp3_path())

    def mp3_path(self):
        filename = md5("%d%f%f" % (
            self.piece.record.id,
            self.piece.start_at,
            self.piece.end_at)).hexdigest()

        return "%s/%s.mp3" % (self.piece.record.folder(), filename)


class Payment(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    price = models.ForeignKey(Price)
    total = models.FloatField()
    status = models.IntegerField()

    owner = models.ForeignKey('auth.User', related_name='user-payments')
    time = models.DateTimeField(auto_now=True)
