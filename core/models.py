#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf import settings

from django.db import models

from core.extra import *
from core.utils import *

import re
import subprocess

from decimal import Decimal

from pydub import AudioSegment

from django.utils import timezone


# class Feedback(models.Model):
#     """
#         Обратная связь

#         owner    - пользователь

#         email    - почта, если не зареган

#         subject - тема

#         text    - текст

#         created - когда создан
#     """

#     owner = models.OneToOneField(User)
#     email = models.CharField(max_length=255)

#     subject = models.CharField(max_length=255, blank=True, null=True)
#     text = models.TextField()

#     created = models.DateTimeField(auto_now=True)


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
        splitted_path = os.path.join(
            settings.MEDIA_ROOT,
            os.path.dirname(self.audio_file_format("mp3")),
            'split')

        # Если нет папки создаём и делим на части
        if not os.path.exists(splitted_path):
            os.makedirs(splitted_path)
            self._split_to_parts(settings.DIARIZATION_PART_SIZE)

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

        return sorted(splitted, lambda x: x[1])

    def _split_to_parts(self, length):
        splitted_path = os.path.join(
            settings.MEDIA_ROOT,
            os.path.dirname(self.audio_file_format("mp3")),
            'split')

        subprocess.call(
            ['mp3splt', '-f',
             '-t', str(length),
             '-a',
             '-d', splitted_path,
             settings.MEDIA_ROOT + self.audio_file_format("mp3")])

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
                 '-ac', str(channels),
                 '-acodec', 'pcm_s16le',
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
            # Если папок нет - создаём
            dir_path = os.path.dirname(settings.MEDIA_ROOT + file_name_format)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

            # Если в таком формате нет, то конвертируем
            subprocess.call(
                ['ffmpeg', '-i',
                 settings.MEDIA_ROOT + original_file_name,
                 '-ac', str(channels),
                 settings.MEDIA_ROOT + file_name_format])

        return file_name_format
