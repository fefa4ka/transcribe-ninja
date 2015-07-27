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
        amount = 0
        completed = 0
        for order in self.orders.all():
            amount += order.queue.all().count()
            completed += order.queue.filter(completed__isnull=False).count()

        if completed > 0:
            return int(float(completed) / amount * 100)
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
        from speaker import Speaker
        from piece import Piece

        position = 0

        record_path = os.path.join(
            settings.MEDIA_ROOT,
            str(self.id))

        voiceid_path = os.path.join(
            record_path,
            'record/diarization/voiceid'
        )

        if not os.path.exists(voiceid_path):
            os.makedirs(voiceid_path)

        # Проверяем, есть ли уже куски
        if self.pieces.count() > 0:
            last_piece = self.pieces.order_by('-end_at')[0]

            if last_piece.end_at + 5 > self.duration:
                shutil.rmtree(record_path, ignore_errors=True)
                return
            else:
                position = last_piece.end_at

        # Загружаем ролик
        # mp3_audio_file = AudioSegment.from_mp3(
        #     settings.MEDIA_ROOT +
        #     self.audio_file_format("mp3")
        # )

        db = GMMVoiceDB(voiceid_path)

        print "Start diarization"

        for part in self.parts:
            audio_file_path = part[0]

            if position > part[1]:
                continue

            position = part[1]
            # Конец куска через определённое время,
            # или если последний кусок — конец записи
            if self.duration > position + settings.DIARIZATION_PART_SIZE * 60:
                end_at = position + settings.DIARIZATION_PART_SIZE * 60
            else:
                end_at = self.duration

            # Куски изначально в mp3, нужно конвертнуть иили нет
            file_name, extension = os.path.splitext(audio_file_path)
            diarization_path = os.path.join(
                record_path,
                'record/diarization')
            wav_audio_file_path = os.path.join(diarization_path, str(position) + ".wav")

            subprocess.call(
                ['ffmpeg', '-i',
                 audio_file_path,
                 '-ac', "2",
                 '-acodec', 'pcm_s16le',
                 '-ar', '16000',
                 wav_audio_file_path])

            print wav_audio_file_path
            # audio_file_path = self.cut_to_file(
            #     os.path.join('diarization', str(position) + ".wav"),
            #     start_at=position, end_at=end_at)

            voice = Voiceid(
                db, wav_audio_file_path)

            # Разрезаем на части
            # Для каждой части делаем сегменты
            # Задача выбрать собеседников

            # Распознаём говорящих
            print "Extract spearkers"
            voice.extract_speakers()

            print "Save pieces"
            # Сохраняем информацию о каждом говоряещм
            for c in voice.get_clusters():
                cluster = voice.get_cluster(c)

                # Каждый кластер - отдельный собеседник
                # Сохраняем информацию о собеседнике. Название и пол
                speaker = Speaker(
                    name=cluster.get_name(), gender=cluster.get_gender())

                speaker.save()

                # Если запись не больше двух часов, то распознаём собеседников на всю запись
                # if self.duration < 2600:
                #     cluster.set_speaker(cluster.get_name())
                #     voice.update_db()

                # Сохраняем все куски, где этот собеседник участвовал
                for segment in cluster.get_segments():
                    piece = Piece(record=self,
                                  start_at=(position + segment.get_start() / 100.0),
                                  end_at=(position + segment.get_end() / 100.0),
                                  duration=segment.get_duration() / 100.0,
                                  speaker=speaker)
                    piece.save()

                    print "Save piece %d to %d" % ((position + segment.get_start() / 100.0), (position + segment.get_end() / 100.0))

        print "Finished"
        # Удаляем все файлы
        shutil.rmtree(record_path, ignore_errors=True)

    def recognize(self):
        """
            Распознаём записи
        """

        for piece in self.pieces.all():
            piece.recognize()
