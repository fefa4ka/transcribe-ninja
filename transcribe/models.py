#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings
# from django.core.files.storage import FileSystemStorage

import os
import time
import re
import subprocess

from datetime import datetime

from decimal import Decimal

from voiceid.sr import Voiceid
from voiceid.db import GMMVoiceDB

import numpy as np

from core.utils import *

from core.extra import *


class Record(models.Model):
    """
    Модель записи, которую стенографируют

    title       - заголовок

    file_name   - аудиофайл записи
    duration    - продолжительность в секундах
    speakers    - количество собеседников

    progress    - на какой стадии находится: никакая, в работе, готов

    owner       - хозяин записи
    created     - когда создана

    """

    title = models.CharField(max_length=200)

    # Файл хранится на Амазоне С3
    file_name = ContentTypeRestrictedFileField(
        max_length=255,
        upload_to=upload_record_path,
        content_types=["audio/mpeg", "audio/vnd.wav"],
        max_upload_size=429916160)

    duration = models.FloatField(default=0)
    speakers = models.IntegerField(default=2)

    # Состояние записи. Без действия, в работе и завершённая.
    PROGRESS_NONE = 0
    PROGRESS_INWORK = 1
    PROGRESS_COMPLETED = 2
    PROGRESS_CHOICES = (
        (PROGRESS_NONE, 0),
        (PROGRESS_INWORK, 1),
        (PROGRESS_COMPLETED, 2)
    )
    progress = models.IntegerField(
        choices=PROGRESS_CHOICES,
        default=PROGRESS_NONE
    )

    # Время создание и принадлежность файла
    owner = models.ForeignKey('auth.User', related_name='records')
    created = models.DateTimeField(auto_now=True)

    # Запись первый раз не удаляется
    trashed_at = models.DateTimeField(blank=True, null=True)

    objects = NonTrashManager()
    trash = TrashManager()

    def __unicode__(self):
        return "Rec %d. %d speakers. %f sec" % (self.id, self.speakers, self.duration)

    # Attributes
    def file_name_format(self, format="mp3"):
        """
            Проверяет, есть ли файл требуемого раширения
        """
        # Расчлиняем на имя файла и расширение
        file_name, extension = os.path.splitext(str(self.file_name))
        file_name_format = file_name + ".%s" % format

        # Если такой файл есть, то возвращаем путь к файлу
        if os.path.isfile(settings.RECORD_ROOT + file_name_format):
            return file_name_format
        else:
            # TODO: сделать конвертацию
            return ""

    def completed_percentage(self):
        """
            Какой процент записи распознан
        """
        # Узнаём длинну частей, которые нужно стенографировать
        duration = np.sum([p.duration for p in self.g_pieces()])

        # Сколько секунд уже стенографировали
        completed_duration = np.sum(
            [t['duration'] for t in self.transcriptions(empty=False)])

        # Если у нас есть все данные, считаем сколько процентов готово
        if duration > 0 and completed_duration > 0:
            return int((100 / duration) * completed_duration)
        else:
            return 0

    def g_pieces(self):
        """
            Части в порядке возрастания
        """
        return Piece.objects.filter(record=self).order_by('start_at')

    def transcriptions(self, empty=True):
        """
            Список транскрибций
        """
        transcriptions = []

        # Собираем транскрипции с  отсортированных по порядку кусков
        for piece in self.g_pieces():
            transcriptions += piece.transcriptions(empty=empty)

        return transcriptions

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

        # Если рааспознали слишком мало, устанавливаем дефолную скорость
        return settings.SPEECH_SPEED if duration < settings.SPEECH_SPEED_MIN_DURATION else speed

    def absolute_url(self):
        return "/record/%i/" % self.id

    def folder(self):
        """
            Название папки
        """
        return os.path.dirname(str(self.file_name))

    # Actions
    def get_file_local(self):
        """
            Путь к файлу записи на локальной машине
        """

        # Скачиваем эмпэтришку с Амазон С3
        s3_record_file = self.file_name
        record_file_name = str(s3_record_file)

        file_path = settings.RECORD_ROOT + record_file_name

        # Если файл есть, ничего не делаем, возращаем путь до него
        if os.path.isfile(file_path):
            return file_path

        # Если папок нет - создаём
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path))

        s3_record_file.open()
        mp3_data = s3_record_file.read()

        # Сохраняем в файл
        mp3_file = open(
            file_path,
            'w+')
        mp3_file.write(mp3_data)
        mp3_file.close()

        return file_path

    def prepare(self):
        """
            Подготовка записи к распознанию
        """
        # Копируем на локальную машину с S3
        self.get_file_local()

        # Конвертируем в mp3 и wav, оригинал удаляем
        self.convert()

        # Получаем длинну записи
        self.duration = self.ffmpeg_length()

        self.save()
        # TODO: Делим на части
        # TODO: Определяем собеседников
        self.liam_diarization()
        self.save()

        # TODO: удалять все ненужные файлы

    def convert(self):
        """
        Конвертируем записи в формат *.mp3 и *.wav
        mp3 для веба
        wav для анализа LIAM, sox
        """
        original_file_name = str(self.file_name)
        file_name, extension = os.path.splitext(str(self.file_name))

        # пробуем конвертить х3ч в wav
        if extension != '.wav':
            subprocess.call(
                ['ffmpeg', '-i',
                 settings.RECORD_ROOT + original_file_name,
                 settings.RECORD_ROOT + file_name + '.wav'])

        # Потом в mp3
        if self.file_name_format('wav') and extension != ".mp3":
            subprocess.call(
                ['ffmpeg', '-i',
                 settings.RECORD_ROOT + original_file_name,
                 settings.RECORD_ROOT + file_name + '.mp3'])

        # Если всё сконвертилось, удаляем оригинал с S3,
        # и копируем mp3
        if "" not in (self.file_name_format('mp3'), self.file_name_format('wav')) and extension != ".mp3":
            os.remove(settings.RECORD_ROOT + original_file_name)

            self.file_name = self.file_name_format('mp3')

    def ffmpeg_length(self):
        """
            Узнаём длину записи в секундах с помощью ffmpeg
        """
        path = settings.RECORD_ROOT + self.file_name_format('wav')

        # Запускаем ffmpeg
        process = subprocess.Popen(
            ['ffmpeg', '-i', path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        stdout, stderr = process.communicate()
        # Вытаскивам данные о длинне
        matches = re.search(
            r"Duration:\s{1}(?P<hours>\d+?):(?P<minutes>\d+?):(?P<seconds>\d+\.\d+?),",
            stdout,
            re.DOTALL).groupdict()

        # Переводим данные в секунды
        hours = Decimal(matches['hours'])
        minutes = Decimal(matches['minutes'])
        seconds = Decimal(matches['seconds'])

        total = 0
        total += 60 * 60 * hours
        total += 60 * minutes
        total += seconds

        return total

    def liam_diarization(self):
        """
            Разделяем запись на собеседников
        """
        # Загружаем ролик
        db = GMMVoiceDB(settings.VOICEID_DB_PATH)
        voice = Voiceid(
            db, settings.RECORD_ROOT + self.file_name_format('wav'))

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

        # for c in voice.get_clusters():
        #     cluster = voice.get_cluster(c)
        #     voice.remove_cluster(cluster.get_name())
        # TO DO: Remove LIAM files

    # Services
    def delete(self, trash=True):
        if not self.trashed_at and trash:
            self.trashed_at = datetime.now()
            self.save()
        else:
            self.file_name.delete()
            super(Record, self).delete()

    def restore(self, commit=True):
        self.trashed_at = None
        if commit:
            self.save()


class Speaker(models.Model):
    """
        Собеседники в записи

        name   - имя
        gender - пол
    """

    name = models.CharField(max_length=255)
    gender = models.CharField(max_length=1)


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

    record = models.ForeignKey(Record)
    start_at = models.FloatField()
    end_at = models.FloatField()
    duration = models.FloatField()
    speaker = models.ForeignKey(Speaker, null=True)

    def transcriptions(self, empty=True):
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

    piece = models.ForeignKey(Piece)
    index = models.IntegerField(default=0)
    text = models.TextField()

    work_type = models.IntegerField(default=0)
    speaker = models.IntegerField(default=0)

    owner = models.ForeignKey('auth.User', related_name='transcription')


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
