#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.utils.http import urlquote

import os
import time

from hashlib import md5


def upload_record_path(instance, file_name):
    """
    Папка и имя записи
    """

    file_name, extension = os.path.splitext(file_name)

    return urlquote("record/%s%s" % (
                    md5(
                        file_name.encode('utf8') + str(time.time())
                    ).hexdigest(),
                    extension))


def upload_export_path(instance, file_name):
    """
    Папка и имя записи
    """

    file_name, extension = os.path.splitext(file_name)

    return urlquote("record/export/%s/%s.%s" % (
                    md5(
                        file_name.encode('utf8') + str(time.time()) + extension
                    ).hexdigest(),
                    file_name,
                    extension))


def upload_queue_path(instance, file_name=""):
    """
        Папка и имя для аудиофрагмента от записи
    """

    filename = md5("%d%s%f%f%f" % (
        instance.piece.record.id,
        instance.piece.record.title.encode('utf8'),
        instance.start_at,
        instance.end_at,
        instance.end_at * instance.start_at)
    ).hexdigest()

    return urlquote("queue/%s.mp3" % (filename))


def upload_piece_path(instance, file_name="", extension="mp3"):
    """
        Папка и имя для аудиофрагмента от записи
    """

    filename = md5("%d%s%f%f" % (
        instance.record.id,
        instance.record.title.encode('utf8'),
        instance.start_at,
        instance.end_at)
    ).hexdigest()

    return urlquote("piece/%s.%s" % (filename, extension))
