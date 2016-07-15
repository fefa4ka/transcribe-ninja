#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf import settings

from django.db import models

from core.extra import *
from core.utils import *

import re
import subprocess

from decimal import Decimal

from django.utils import timezone

from django.contrib.auth.models import User

import collections

import contextlib

import webrtcvad

import wave


class Feedback(models.Model):
    """
        Обратная связь

        owner    - пользователь

        email    - почта, если не зареган

        subject - тема

        text    - текст

        created - когда создан
    """

    owner = models.ForeignKey(User, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True, null=True)

    subject = models.CharField(max_length=255, blank=True, null=True)
    text = models.TextField(blank=True, null=True)

    created = models.DateTimeField(auto_now=True)


class Language(models.Model):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=255)
    english_name = models.CharField(max_length=255)

    def __str__(self):
        return self.english_name


class Trash(models.Model):
    # Чтобы запись не удалялась с первого раза
    trashed_at = models.DateTimeField(blank=True, null=True)

    objects = NonTrashManager()
    trash = TrashManager()

    class Meta:
        abstract = True

    def __str__(self):
        trashed = (self.trashed_at and 'trashed' or 'not trashed')
        return '%d (%s)' % (self.id, trashed)

    def delete(self, trash=True):
        if not self.trashed_at and trash:
            self.trashed_at = timezone.now()
            self.save()
        else:
            super(SomeModel, self).delete()

    def restore(self, commit=True):
        self.trashed_at = None
        if commit:
            self.save()


class AudioFile(models.Model):
    class Meta:
        abstract = True

    def audio_file_format(self, audio_format="mp3", channels=2):
        """
            Проверяет, есть ли файл требуемого раширения
        """
        # Расчлиняем имя на имя файла и расширение
        original_file_name = self.audio_file_local()
        file_name, extension = os.path.splitext(original_file_name)

        # Имя файла в новрм формате
        file_name_format = file_name + ".%s" % audio_format

        return self._ffmpeg_decode(original_file_name, file_name_format, channels)


    def audio_file_local(self):
        """
            Путь к файлу записи на локальной машине
        """

        # Скачиваем эмпэтришку с Амазон С3
        record_file_name = os.path.join(
            str(self.id),
            str(self.audio_file)
        )

        file_path = settings.MEDIA_ROOT + record_file_name

        # Если файл есть, ничего не делаем, возращаем путь до него
        if os.path.isfile(file_path):
            return record_file_name

        # Если папок нет - создаём
        dir_path = os.path.dirname(file_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        # Скачиваем мп3
        self.audio_file.open()
        mp3_data = self.audio_file.read()

        # Сохраняем в файл
        mp3_file = open(
            file_path,
            'w+')
        mp3_file.write(mp3_data)
        mp3_file.close()

        return record_file_name

    def audio_file_length(self):
        """
            Узнаём длину записи в секундах с помощью ffmpeg
        """
        path = settings.MEDIA_ROOT + self.audio_file_format('mp3')

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

    @property
    def parts(self):
        return self.mp3splt_parts

    @property
    def vad_parts(self):
        vad = webrtcvad.Vad(0)
        audio, sample_rate = self._read_wav()
        frames = self._frame_generator(30)
        frames = list(frames)
        segments = self._vad_collector(sample_rate, 30, 300, vad, frames)

        return segments
        # Glue
        # Minimum piece lenght = 5 seconds
        # Maximum piece lenght = 15 seconds
        glued = []
        for index, seg in enumerate(segments):
            duration = seg[1] - seg[0]

            previous_seg = segments[index - 1]
            previous_silence = seg[0] - previous_seg[1]

            if len(segments) - 1 > index:
                next_seg = segments[index + 1]
                next_silence = next_seg[0] - seg[1]
            else:
                next_seg = seg
                next_silence = duration


            if duration > settings.PIECE_DURATION_MINIMUM and duration < settings.PIECE_DURATION_MAXIMUM:
                if to_glue:
                    seg[0] = to_glue
                    to_glue = False

                glued.append(seg)
                next

            if duration < settings.PIECE_DURATION_MINIMUM:
                # Приклеиваем козявку к ближайшему подходящему
                if len(glued) > 0 and previous_silence < duration and (seg[1] - previous_seg[0]) < settings.PIECE_DURATION_MAXIMUM:
                    glued[len(glued) - 1][1] = seg[1]
                elif next_silence < duration and (next_seg[1] - seg[0]) < settings.PIECE_DURATION_MAXIMUM:
                    to_glue = seg[0]
                else:
                    glued.append(seg)

        return glued

    @property
    def mp3splt_parts(self):
        splitted_path = os.path.join(
            settings.MEDIA_ROOT,
            os.path.dirname(self.audio_file_format("mp3")),
            'split')

        # Если нет папки создаём и делим на части
        if not os.path.exists(splitted_path):
            os.makedirs(splitted_path)
            subprocess.call(
                ['mp3splt', '-f',
                 '-t', str(settings.DIARIZATION_PART_SIZE),
                 '-a',
                 '-d', splitted_path,
                 settings.MEDIA_ROOT + self.audio_file_format("mp3")])

        # Если есть, надеемся, что там все файлы
        files = os.listdir(splitted_path)

        splitted = []
        # Создаём массив из файлов и тайминга
        for mp3_name in files:
            name_start_at, end_at_ext = mp3_name.split('__')
            name, start_at_min, start_at_sec = name_start_at.split('_')
            end_at, ext = end_at_ext.split('.')

            try:
                end_at_min, end_at_sec = end_at.split('_')
            except:
                end_at_min, end_at_sec, total = end_at.split('_')

            start_at = int(start_at_min[0:-1]) * 60 + int(start_at_sec[0:-1])
            end_at = int(end_at_min[0:-1]) * 60 + int(end_at_sec[0:-1])

            splitted.append([
                os.path.join(splitted_path, mp3_name),
                start_at,
                end_at])

        return sorted(splitted, key=lambda x: x[1])


    def cut_to_file(self, file_name, start_at, end_at, offset=0, channels=2):
        """
            Создаёт вырезанный кусок в mp3

            rec - можно передать AudioSegment записи, чтобы ускорить процесс
            offset  - сколько записи по краям оставлять
        """
        original_file_name, extension = os.path.splitext(file_name)

        parts = self.parts

        # Файл записи
        if extension == "mp3":
            audio_file_path = final_file_path = os.path.join(
                str(self.id),
                file_name
            )
        else:
            audio_file_path = os.path.join(
                str(self.id),
                original_file_name + ".mp3"
            )
            final_file_path = os.path.join(
                str(self.id),
                file_name
            )

        audio_dir_path = os.path.dirname(settings.MEDIA_ROOT + audio_file_path)

        if not os.path.isfile(settings.MEDIA_ROOT + audio_dir_path):
            # Создаём папку, если её не было
            if not os.path.exists(audio_dir_path):
                os.makedirs(audio_dir_path)

            # В первой записи делаем отступ максмум до 0
            if start_at > offset:
                start_at = (start_at - offset)
            else:
                start_at = 0

            # В последней не больше, чем длинна записи
            if end_at + offset > self.duration:
                end_at = self.duration
            else:
                end_at = (end_at + offset)

        # Опредеяем в какой части находится нужный кусок и оттуда вырезаем
        for part in parts:
            mp3_file = part[0]
            part_start_at = part[1]
            part_end_at = part[2]

            # Т.к. диаризируются эти же куски, большинство
            # частей окажется в них
            if start_at >= part_start_at and part_end_at >= end_at:
                print "Part %d-%d.  Queue %d-%d" % (part_start_at, part_end_at, start_at, end_at)

                subprocess.call(
                    ['ffmpeg', '-i',
                     mp3_file,
                     '-vcodec', 'copy',
                     '-ss', str(start_at - part_start_at),
                     '-t', str((end_at - start_at)),
                     settings.MEDIA_ROOT + audio_file_path])

        # Но может склеится два куска и они окажутся в разных записях,
        # на этот случай вырезаем из одного куска (это долго, если часть в конце а запись большая)
        if not os.path.exists(settings.MEDIA_ROOT + audio_file_path):
            subprocess.call(
                ['ffmpeg', '-i',
                 settings.MEDIA_ROOT + self.audio_file_format("mp3"),
                 '-vcodec', 'copy',
                 '-ss', str(start_at),
                 '-t', str((end_at - start_at)),
                 settings.MEDIA_ROOT + audio_file_path])

        # Выдаём нужный формат
        if extension == "wav":
            subprocess.call(
                ['ffmpeg', '-i',
                 settings.MEDIA_ROOT + audio_file_path,
                 '-acodec', 'pcm_s16le',
                 '-ac', str(channels),
                 '-ar', '16000',
                 settings.MEDIA_ROOT + final_file_path])
        elif extension != "mp3":
            audio_file_path = self._ffmpeg_decode(
                original_file_name=audio_file_path,
                file_name_format=final_file_path,
                channels=channels
            )
            # TODO: удалить ненужный файл mp3
        return audio_file_path

    def _ffmpeg_decode(self, original_file_name, file_name_format, channels=2):
        # Если такой файл есть, то возвращаем путь к файлу
        if not os.path.isfile(settings.MEDIA_ROOT + file_name_format):
            file_name_format_title, extension = os.path.splitext(file_name_format)

            # Если папок нет - создаём
            dir_path = os.path.dirname(settings.MEDIA_ROOT + file_name_format)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

            # Если в таком формате нет, то конвертируем
            print extension
            if extension == ".wav":
                print "WOOgoGO"
                subprocess.call(
                    ['ffmpeg', '-i',
                     settings.MEDIA_ROOT + original_file_name,
                     '-acodec', 'pcm_s16le',
                     '-ac', str(channels),
                     '-ar', '16000',
                     settings.MEDIA_ROOT + file_name_format])
            else:
                subprocess.call(
                    ['ffmpeg', '-i',
                     settings.MEDIA_ROOT + original_file_name,
                     '-ac', str(channels),
                     settings.MEDIA_ROOT + file_name_format])

        return file_name_format

    def _read_wav(self):
        wav_file = os.path.join(
            settings.MEDIA_ROOT,
            self.audio_file_format("wav", channels=1)
        )

        with contextlib.closing(wave.open(wav_file, 'rb')) as wf:
            num_channels = wf.getnchannels()
            assert num_channels == 1
            sample_width = wf.getsampwidth()
            assert sample_width == 2
            sample_rate = wf.getframerate()
            assert sample_rate in (8000, 16000, 32000)
            pcm_data = wf.readframes(wf.getnframes())
            return pcm_data, sample_rate

    def _frame_generator(self, frame_duration_ms):
        audio, sample_rate = self._read_wav()

        n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
        offset = 0
        while offset + n < len(audio):
            yield audio[offset:offset + n]
            offset += n

    def _vad_collector(self, sample_rate, frame_duration_ms, padding_duration_ms, vad, frames):
        num_padding_frames = int(padding_duration_ms / frame_duration_ms)
        ring_buffer = collections.deque(maxlen=num_padding_frames)
        triggered = False

        voices = []
        time_start = 0
        time_end = 0
        # silence = 0

        for index, frame in enumerate(frames):
            time = index * int(sample_rate * (frame_duration_ms / 1000.0) * 2)\
                    / (sample_rate * 2.)

            if not triggered:
                ring_buffer.append(frame)
                num_voiced = len([f for f in ring_buffer
                                  if vad.is_speech(f, sample_rate)])
                if num_voiced > 0.9 * ring_buffer.maxlen:
                    triggered = True
                    ring_buffer.clear()

                    # silence += time - time_end
                    time_start = time
            else:
                ring_buffer.append(frame)
                num_unvoiced = len([f for f in ring_buffer
                                    if not vad.is_speech(f, sample_rate)])
                if num_unvoiced > 0.9 * ring_buffer.maxlen:
                    triggered = False
                    ring_buffer.clear()

                    time_end = time

                    segment = [time_start, time_end]
                    voices.append(segment)
                    # print '%.2f - %.2f to %.2f sec' % (time_end - time_start, time_start, time_end)
                    time_start = time

        return voices


