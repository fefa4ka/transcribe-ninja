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

    return urlquote("record/%s/%s%s" % (md5(folder).hexdigest(),
                                 md5(file_name).hexdigest(),
                                 extension))

@job('diarization')
def record_prepare(record):
    record.prepare()
