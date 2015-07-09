#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db import models

from core.utils import *
from core.models import *
from core.extra import *

from speaker import Speaker

from piece import Piece

from libs.RemoteTypograf import RemoteTypograf


class Transcription(models.Model):

    """
        Транскрипция. Относится к какому-то куску.
        Транскрипций для куска может быть несколько.

        piece       - кусок
        index       - порядок в куске
        text        - транскрибция

        work_type   - в результате чего появилась транскрибция
                      Queue.TRANSCRIBE - транскрибция
                      Queue.CHECK      - проверка

        speaker     - какому собеседнику пренадлежит высказывание

        owner       - кто это сделал
    """

    piece = models.ForeignKey(Piece, related_name='all_transcriptions')
    index = models.IntegerField(default=0)
    text = models.TextField()

    work_type = models.IntegerField(default=0)
    speaker_code = models.CharField(max_length=2)
    speaker = models.ForeignKey(Speaker, related_name='transcriptions')

    queue = models.ForeignKey('work.Queue', related_name='transcriptions')

    @property
    def start_at(self):
        return self.piece.start_at if self.index == 0\
            else self.previous.end_at

    @property
    def end_at(self):
        return self.start_at + len(self.text) * self.piece.letters_per_sec

    @property
    def text_pretty(self):
        # Правим типографику
        rt = RemoteTypograf()
        rt.noEntities()
        rt.p(0)
        rt.br(0)
        rt.nobr(0)
        text = rt.prettyText(self.text)
        text = rt.processText(text.encode('utf-8'))

        return text.decode('utf-8')

    @property
    def name(self):
        if self.speaker:
            return self.speaker
        else:
            return self.piece.speaker.name

        # print speaker
        # # Если нет имени
        # # Проверяем, входит ли в основной набор собеседников
        # if not speaker.name:
        #     # Если да, и собеседников двое
        #     # то имена «Женщина» или «Мужчина»
        #     name = "Female" if speaker.gender == "F" else "Male"

        # return speaker.name

    @property
    def gender(self):
        if self.speaker_code:
            return self.speaker_code[0]

        return self.piece.speaker.gender

    @property
    def previous(self):
        """
            Предыдущий кусок
        """

        transcription = Transcription.objects.\
            filter(piece=self.piece, index__exact=self.index - 1)

        if not transcription:
            return None

        return transcription[0]

    @property
    def next(self):
        """
            Кусок следующий после этого
        """

        transcription = Transcription.objects.\
            filter(piece=self.piece, index__exact=self.index + 1)

        if not transcription:
            return None

        return transcription[0]
