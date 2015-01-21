#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.core.files import File

import os
import time
import shutil

from voiceid.sr import Voiceid
from voiceid.db import GMMVoiceDB

import numpy as np

from core.utils import *
from core.models import *
from core.extra import *


class Record(AudioFile, Trash):

    """
    Модель записи, которую стенографируют

    title       - заголовок

    audio_file  - аудиофайл записи
    duration    - продолжительность в секундах
    speakers    - количество собеседников

    progress    - на какой стадии находится: никакая, в работе, готов

    owner       - хозяин записи
    created     - когда создана

    """

    title = models.CharField(max_length=200)
    audio_file = models.FileField(
        max_length=255,
        upload_to=upload_record_path)

    duration = models.FloatField(default=0)
    speakers = models.IntegerField(default=2)

    # Состояние записи. Без действия, в работе и завершённая.
    PROGRESS_NONE = 0
    PROGRESS_INWORK = 1
    PROGRESS_COMPLETED = 2
    PROGRESS_CHOICES = (
        (PROGRESS_NONE, 'Uploaded'),
        (PROGRESS_INWORK, 'In progress'),
        (PROGRESS_COMPLETED, 'Completed')
    )
    progress = models.IntegerField(
        choices=PROGRESS_CHOICES,
        default=PROGRESS_NONE
    )

    # Время создание и принадлежность файла
    owner = models.ForeignKey('auth.User', related_name='records')
    created = models.DateTimeField(auto_now=True)


    # Не отображать в названии utf-8, потому что django-rq ругается
    def __unicode__(self):
        return "%d: %d sec" % (self.id, self.duration)

    # Список транскрибций
    @property
    def transcriptions(self):
        """
            Список транскрибций
        """
        transcriptions = []

        # Собираем транскрипции с  отсортированных по порядку кусков
        for piece in self.pieces.all():
            transcriptions += piece.transcriptions.all().order_by('index')

        return transcriptions

    @property
    def completed(self):
        """
            Какой процент записи распознан
        """
        # Узнаём длинну частей, которые нужно стенографировать
        duration = np.sum([p.duration for p
                           in self.pieces.all().order_by('start_at')])

        # Сколько секунд уже стенографировали
        # completed_duration = np.sum(
        #     [t['duration'] for t in self.transcriptions(empty=False)])
        from django.db.models import Count

        completed_pieces = self.pieces\
            .annotate(transcriptions_count=Count('transcriptions'))\
            .filter(transcriptions_count__gt=0)

        completed_duration = np.sum(
            [piece.end_at - piece.start_at for piece in completed_pieces])

        # Если у нас есть все данные, считаем сколько процентов готово
        if duration > 0 and completed_duration > 0:
            return int((100 / duration) * completed_duration)
        else:
            return 0

    @property
    def speed(self):
        """
            Скорость печати. Знаков в секунду.
        """
        duration = 0
        length = 0
        speed = 0

        # Считаем общую длинну стенографированного текста и время
        for t in self.transcriptions(empty=False):
            length += len(t['text'])
            duration += t['end'] - t['start']

        # Если хотя бы что-то рапознали, считаем
        if duration > 0:
            speed = length / duration

        # Если рааспознали слишком мало, устанавливаем дефолтную скорость
        return settings.SPEECH_SPEED if duration < settings.SPEECH_SPEED_MIN_DURATION else speed

    # Actions

    def prepare(self):
        """
            Подготовка записи к раздаче и к распознанию.
        """

        # Конвертируем в mp3 и сохраняем как оригинал
        # если файл загружен в каком-то другом формате
        mp3_file = self.audio_file_format("mp3")

        # Считываем продолжительность записи.
        # Нужно именно здесь, потому что файл уже скачен и отконвертирован.
        # Если заменить, то придётся заново запись скачивать с хранилища
        self.duration = self.audio_file_length()

        if self.audio_file_local() != mp3_file:
            # Заменяем оригинал на мп3
            self.audio_file.delete()
            self.audio_file.save(
                mp3_file,
                File(
                    open(settings.MEDIA_ROOT + mp3_file)
                )
            )

        # Удаляем все файлы
        shutil.rmtree(
            os.path.dirname(settings.MEDIA_ROOT + mp3_file),
            ignore_errors=True)

    def diarization(self):
        """
            Разделяем запись на собеседников
        """

        # Загружаем ролик
        audio_file_path = settings.MEDIA_ROOT + self.audio_file_format('wav')

        db = GMMVoiceDB(settings.VOICEID_DB_PATH)
        voice = Voiceid(
            db, audio_file_path)

        # Распознаём говорящих
        voice.extract_speakers()

        # Сохраняем информацию о каждом говоряещм
        for c in voice.get_clusters():
            cluster = voice.get_cluster(c)

            # Каждый кластер - отдельный собеседник
            # Сохраняем информацию о собеседнике. Название и пол
            speaker = Speaker(
                name=cluster.get_name(), gender=cluster.get_gender())
            speaker.save()

            # Сохраняем все куски, где этот собеседник участвовал
            for segment in cluster.get_segments():
                piece = Piece(record=self,
                              start_at=segment.get_start() / 100,
                              end_at=segment.get_end() / 100,
                              duration=segment.get_duration() / 100,
                              speaker=speaker)
                piece.save()

        # Удаляем все файлы
        shutil.rmtree(
            os.path.dirname(audio_file_path),
            ignore_errors=True)


class Speaker(models.Model):

    """
        Собеседники в записи

        name   - имя
        gender - пол
    """

    name = models.CharField(max_length=255)
    gender = models.CharField(max_length=1)

    def __unicode__(self):
        return "%s: %s" % (self.gender, self.name)


class Piece(models.Model):

    """
        Часть записи

        record    - запись

        start_at  - начала куска, относительно записи
        end_at    - конец куска, относительно записи
        duration  - продолжительность куска

        speaker   - собеседник в куске

        transcriptions()       - танскрибции этого куска
        transcriptions_count() - количество транскрибций
    """

    record = models.ForeignKey(Record, related_name='pieces')
    start_at = models.FloatField()
    end_at = models.FloatField()
    duration = models.FloatField()
    speaker = models.ForeignKey(Speaker, blank=True, null=True)

    def __unicode__(self):
        return "%d-%d sec" % (self.start_at, self.end_at)

    @property
    def previous(self):
        """
            Предыдущий кусок
        """

        piece = Piece.objects.filter(
            end_at__lte=self.start_at).order_by('-end_at')

        if not piece:
            return None

        return piece[0]

    @property
    def next(self):
        """
            Кусок следующий после этого
        """

        piece = Piece.objects.filter(
            start_at__gte=self.end_at).order_by('start_at')

        if not piece:
            return None

        return piece[0]

    @property
    def letters_per_sec(self):
        return self.duration / \
            np.sum([len(t.text) for t in self.transcriptions.all()])

    def g_transcriptions(self, empty=True):
        transcriptions = []

        p_transcriptions = Transcription.objects.filter(
            piece=self).order_by('index')
        start_at = self.start_at

        speed = [0.1]

        if self.transcriptions_count() > 0:
            piece_duration_per_sec = self.duration / \
                np.sum([len(t.text) for t in p_transcriptions])

            speed.append(piece_duration_per_sec)

            for t in p_transcriptions:
                end_at = start_at + len(t.text) * piece_duration_per_sec
                transcriptions.append({
                    'start': start_at,
                    'end': end_at,
                    'duration': end_at - start_at,
                    'timestamp': time.strftime("%H:%M:%S", time.gmtime(start_at)),
                    'text': t.text
                })

                start_at = end_at
        else:
            if empty:
                length = (self.end_at - start_at) * (1 / np.average(speed))

                text = ["_"] * int(length)
                for w in range(int(length / 5)):
                    index = np.random.random_integers(0, length - 1)
                    text[index] = " "

                transcriptions.append({
                    'start': float(start_at),
                    'end': float(self.end_at),
                    'duration': float(self.end_at) - float(start_at),
                    'timestamp': time.strftime(
                        "%H:%M:%S",
                        time.gmtime(start_at)
                    ),
                    'text': "".join(text)
                })

        return transcriptions

    def transcriptions_count(self):
        return Transcription.objects.filter(
            piece=self).order_by('index').count()


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

    piece = models.ForeignKey(Piece, related_name='transcriptions')
    index = models.IntegerField(default=0)
    text = models.TextField()

    work_type = models.IntegerField(default=0)
    speaker = models.IntegerField(default=0)

    queue = models.ForeignKey('work.Queue', related_name='transcriptions')

    @property
    def start_at(self):
        return self.piece.start_at if self.index == 0\
            else self.previous.end_at

    @property
    def end_at(self):
        return self.start_at + len(self.text) * self.piece.letters_per_sec()

    @property
    def previous(self):
        """
            Предыдущий кусок
        """

        transcription = Transcription.objects.filter(piece=self.piece, index__exact=self.index - 1)

        if not transcription:
            return None

        return transcription[0]

    @property
    def next(self):
        """
            Кусок следующий после этого
        """

        transcription = Transcription.objects.filter(piece=self.piece, index__exact=self.index + 1)

        if not transcription:
            return None

        return transcription[0]


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
