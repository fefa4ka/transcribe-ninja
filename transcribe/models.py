#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db import models
# from django.conf import settings
# from django.core.files import File

# import os
# import time
# import shutil

# import urllib2

# from xml.dom.minidom import parseString as XMLParse

# from datetime import datetime

# from voiceid.sr import Voiceid
# from voiceid.db import GMMVoiceDB

# import numpy as np

# from core.utils import *
# from core.models import *
# from core.extra import *

# from pydub import AudioSegment
from record import Record

from piece import Piece

from transcription import Transcription

class Logs(models.Model):

    """
        Логи о том, как делали транскрибцию.

        transcription   - транскрибция

        play_log        - плей, пауза, перемотка
        key_log         - какие клавиши нажимали
        mouse_log       - как пользовались мышкой

        start_at        - когда началась транскрибция
        end_at          - когда закончилась

        platform        - откуда делали
    """
    transcription = models.ForeignKey(Transcription)

    play_log = models.TextField()
    key_log = models.TextField()
    mouse_log = models.TextField()

    start_at = models.DateTimeField()
    end_at = models.DateTimeField(auto_now=True)

    platform = models.CharField(max_length=255)
