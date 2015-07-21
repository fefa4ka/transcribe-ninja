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

    @property
    def export_name(self):
        # Для N самых используемых собеседников пишем
        # Мужчина 1, Мужчина 2, Женщина 1
        # Для остальных "Неизвестный собеседник мужчина"
        piece = self.piece
        record = piece.record
        speakers_in_record = Piece.objects.filter(record=record).values('speaker_id').annotate(count=models.Count('id')).order_by('-count')[:record.speakers]
        speakers_in_piece = piece.transcriptions.values_list('speaker_code', flat=True).distinct()

        females = 0
        males = 0

        speaker_gender = u"Женщина" if self.speaker_code[0] == "F"\
                                    else u"Мужчина"

        # Проверяем, есть ли говорящий в транскрибции в часто встречаемых собседениках всей записи
        for speaker_stat in speakers_in_record:
            speaker_id = speaker_stat['speaker_id']
            speaker = Speaker.objects.get(id=speaker_id)

            # Получаем его номер (может быть несколько собеседников одного пола)
            if speaker.gender == "F":
                females += 1
            else:
                males += 1

            # Если собеседник такой есть и в транскрибции не встречается других
            # То называем его по полу и номеру «Основной собседеник женщина №1»
            if speaker_id == piece.speaker.id:
                # Если только один собеседник в куске
                # TODO: Если это самая большая часть из всех транскрибциий
                # TODO: Или эта часть единственная совпадает по полу
                # Или собеседник того же пола и индекс 1
                # То собеседник такойже
                if speakers_in_piece.count() == 1\
                    or (speaker.gender == self.speaker_code[0] and self.speaker_code[1] == 1):

                    speaker_index = females if speaker.gender == "F"\
                                            else males

                    return u"Основной собеседник %s %d" % (speaker_gender, speaker_index)
                else:
                    return u"Неизвестный собеседник %s" % (speaker_gender)
            else:
                return u"Неизвестный собеседник %s" % (speaker_gender)
        # Проверяем сколько мужчин
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
