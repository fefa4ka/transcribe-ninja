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
                        file_name.encode('utf8'),
                        time.time()
                    ).hexdigest(),
                    extension))


def upload_queue_path(instance, file_name):
    """
        Папка и имя для аудиофрагмента от записи
    """

    filename = md5("queue/%d%f%f%f" % (
        instance.piece.record.id,
        instance.start_at(),
        instance.end_at())
    ).hexdigest()

    return urlquote("%s.mp3" % (filename))
