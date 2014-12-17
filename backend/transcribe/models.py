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

from utils import *

from backend.core.extra import *


class Record(models.Model):
    # fs = FileSystemStorage(location=settings.RECORD_ROOT)

    title = models.CharField(max_length=200)
    file_name = ContentTypeRestrictedFileField(
        upload_to=upload_record_path,
        content_types=["audio/mpeg", "audio/vnd.wav"],
        max_upload_size=429916160)
    duration = models.FloatField(default=0)
    speakers = models.IntegerField(default=2)
    progress = models.IntegerField(default=0)

    time = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey('auth.User', related_name='records')

    trashed_at = models.DateTimeField(blank=True, null=True)

    objects = NonTrashManager()
    trash = TrashManager()

    def delete(self, trash=True):
        if not self.trashed_at and trash:
            self.trashed_at = datetime.now()
            self.save()
        else:
            # self.file_name.delete()
            super(Record, self).delete()

    def restore(self, commit=True):
        self.trashed_at = None
        if commit:
            self.save()

    def file_name_format(self, format="mp3"):
        file_name, extension = os.path.splitext(str(self.file_name))
        file_name_format = file_name + ".%s" % format

        if os.path.isfile(settings.RECORD_ROOT + file_name_format):
            return file_name_format
        else:
            return ""

    def time_length(self):
        return time.strftime("%H:%M:%S", time.gmtime(self.duration))

    def completed_percentage(self):
        duration = np.sum([p.duration for p in self.g_pieces()])
        completed_duration = np.sum(
            [t['duration'] for t in self.transcriptions(empty=False)])

        if duration > 0 and completed_duration > 0:
            return int((100 / duration) * completed_duration)
        else:
            return 0

    def g_pieces(self):
        return Piece.objects.filter(record=self).order_by('start_at')

    def transcriptions(self, empty=True):
        transcriptions = []

        for piece in self.g_pieces():
            transcriptions += piece.transcriptions(empty=empty)

        return transcriptions

    def speed(self):
        duration = 0
        length = 0
        speed = 0

        for t in self.transcriptions(empty=False):
            length += len(t['text'])
            duration += t['end'] - t['start']

        if duration > 0:
            speed = length / duration

        return 22 if duration < 120 else speed

    def absolute_url(self):
        return "/record/%i/" % self.id

    def folder(self):
        return os.path.dirname(str(self.file_name))

    def __unicode__(self):
        return "%d speakers. %f sec" % (self.speakers, self.duration)

    def prepare(self):
        """
        Подготовка записи к распознанию
        """

        # Конвертируем в mp3 и wav, оригинал удаляем
        self.convert()

        # Получаем длинну записи
        self.duration = self.ffmpeg_length()

        self.save()
        # TODO: Делим на части
        # TODO: Определяем собеседников
        self.liam_diarization()
        self.save()

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

        # Если всё сконвертилось, удаляем оригинал
        # и ставим mp3 как основное название
        if "" not in (self.file_name_format('mp3'), self.file_name_format('wav')) and extension != ".mp3":
            os.remove(settings.RECORD_ROOT + original_file_name)

            self.file_name = self.file_name_format('mp3')

    def ffmpeg_length(self):
        path = settings.RECORD_ROOT + self.file_name_format('wav')

        process = subprocess.Popen(
            ['ffmpeg', '-i', path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, stderr = process.communicate()
        matches = re.search(
            r"Duration:\s{1}(?P<hours>\d+?):(?P<minutes>\d+?):(?P<seconds>\d+\.\d+?),", stdout, re.DOTALL).groupdict()

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
        """
        db = GMMVoiceDB('backend/transcribe/voiceid')
        voice = Voiceid(
            db, settings.RECORD_ROOT + self.file_name_format('wav'))

        # Распознаём говорящих
        voice.extract_speakers()

        # Сохраняем информацию о каждом говоряещм
        for c in voice.get_clusters():
            cluster = voice.get_cluster(c)

            speaker = Speaker(
                name=cluster.get_name(), gender=cluster.get_gender())
            speaker.save()

            for segment in cluster.get_segments():
                piece = Piece(record=self,
                              start_at=segment.get_start() / 100, end_at=segment.get_end() / 100,
                              duration=segment.get_duration() / 100,
                              speaker=speaker)
                piece.save()

        # for c in voice.get_clusters():
        #     cluster = voice.get_cluster(c)
        #     voice.remove_cluster(cluster.get_name())
        # TO DO: Remove LIAM files


class Speaker(models.Model):
    name = models.CharField(max_length=255)
    gender = models.CharField(max_length=1)


class Piece(models.Model):
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
                    'timestamp': time.strftime("%H:%M:%S", time.gmtime(start_at)),
                    'text': "".join(text)
                })

        return transcriptions

    def transcriptions_count(self):
        return Transcription.objects.filter(piece=self).order_by('index').count()


class Transcription(models.Model):
    piece = models.ForeignKey(Piece)
    text = models.TextField()
    index = models.IntegerField(default=0)

    work_type = models.IntegerField(default=0)
    speaker = models.IntegerField(default=0)

    owner = models.ForeignKey('auth.User', related_name='transcription')
    time = models.DateTimeField(auto_now=True)


class Logs(models.Model):
    transcription = models.ForeignKey(Transcription)
    play_log = models.TextField()
    key_log = models.TextField()
    mouse_log = models.TextField()
    start_at = models.DateTimeField()
    end_at = models.DateTimeField(auto_now=True)
    platform = models.CharField(max_length=255)
