#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.core.files import File

import os
import shutil

from voiceid.sr import Voiceid
from voiceid.db import GMMVoiceDB

import numpy as np

from core.utils import *
from core.models import *
from core.extra import *

from pydub import AudioSegment

from speaker import Speaker


class Record(AudioFile, Trash):

    """
    Модель записи, которую стенографируют

    title       - заголовок

    audio_file  - аудиофайл записи
    duration    - продолжительность в секундах
    speakers    - количество собеседников
    language    - локаль записи

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
    language = models.CharField(max_length=20, default="ru-RU")

    # Состояние записи. Без действия, в работе и завершённая.
    PROGRESS_NONE = 0
    PROGRESS_DIARIZED = 1
    PROGRESS_ORDERED = 2
    PROGRESS_INWORK = 3
    PROGRESS_COMPLETED = 4
    PROGRESS_CHOICES = (
        (PROGRESS_NONE, 'Uploaded'),
        (PROGRESS_ORDERED, 'Ordered'),
        (PROGRESS_DIARIZED, 'Diarized'),
        (PROGRESS_INWORK, 'Recognizing'),
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

    @property
    def order(self):
        for order in self.orders.all():
            return order.created

    # Список транскрибций
    @property
    def transcriptions(self):
        """
            Список транскрибций
        """
        transcriptions = []

        # Собираем транскрипции с  отсортированных по порядку кусков
        for piece in self.pieces.all().order_by('start_at'):
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
            .annotate(transcriptions_count=Count('all_transcriptions'))\
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
        for transcription in self.transcriptions:
            length += len(transcription.text)
            duration += transcription.end_at - transcription.start_at

        # Если хотя бы что-то рапознали, считаем
        if duration > 0:
            speed = length / duration

        # Если рааспознали слишком мало, устанавливаем дефолтную скорость
        return settings.SPEECH_SPEED\
            if duration < settings.SPEECH_SPEED_MIN_DURATION\
            else speed

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

        # Проверяем, есть ли уже куски
        if self.pieces.count() > 0:
            return

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
                print segment.get_start()
                piece = Piece(record=self,
                              start_at=segment.get_start() / 100.0,
                              end_at=segment.get_end() / 100.0,
                              duration=segment.get_duration() / 100.0,
                              speaker=speaker)
                piece.save()

        # Удаляем все файлы
        shutil.rmtree(
            os.path.dirname(audio_file_path),
            ignore_errors=True)

    def recognize(self):
        """
            Распознаём записи
        """
        as_record = AudioSegment.from_mp3(
            settings.MEDIA_ROOT +
            self.audio_file_format("mp3")
        )

        for piece in self.pieces.all():
            piece.recognize(as_record=as_record)
