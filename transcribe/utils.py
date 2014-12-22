#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf import settings
from django.utils.http import urlquote

import os

from hashlib import md5

from django_rq import job


def upload_record_path(instance, file_name):
    """
    Папка и имя записи
    """

    file_name, extension = os.path.splitext(file_name)
    folder = instance.title.encode('utf-8') + file_name.encode('utf-8')

    return urlquote("record/%s/%s%s" % (
                    md5(folder).hexdigest(),
                    md5(file_name).hexdigest(),
                    extension))


def upload_queue_path(instance, file_name):
    filename = md5("%d%f%f%f" % (
        instance.piece.record.id,
        instance.piece.record.folder(),
        instance.start_at(),
        instance.end_at())
    ).hexdigest()

    return urlquote("%s.mp3" % (filename))


@job('diarization')
def record_prepare(record):
    record.prepare()


@job('web')
def record_save(serializer, owner):
    serializer.save(owner=owner)
