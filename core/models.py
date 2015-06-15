#!/usr/bin/python
# -*- coding: utf-8 -*-

import django.db.models.signals as signals

from django.conf import settings

from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum

from core.extra import *
from core.utils import *

import re
import subprocess

from decimal import Decimal

from pydub import AudioSegment


class Account(models.Model):
    """
        Расширенная информация по учётной записи

        user    - пользователь

        phone   - номер телефона

        raing   - рейтинг

        balance - баланс
    """

    user = models.OneToOneField(User)

    phone = models.CharField(max_length=50, blank=True, null=True)

    rating = models.FloatField(default=0)
    balance = models.FloatField(default=0)
    site = models.CharField(max_length=50)

    @property
    def work_length(self):
        try:
            work = self.user.queue.all().aggregate(work=Sum('work_length'))
            mistakes = self.user.queue.all().aggregate(mistakes=Sum('mistakes_length'))

            return work['work'] - mistakes['mistakes']
        except:
            return 0



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
            self.trashed_at = datetime.now()
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

    def cut_to_file(self, file_name, start_at, end_at, as_record=None, offset=1.5, channels=2):
        """
            Создаёт вырезанный кусок в mp3

            rec - можно передать AudioSegment записи, чтобы ускорить процесс
            offset  - сколько записи по краям оставлять
        """
        original_file_name, extension = os.path.splitext(file_name)

        if not as_record:
            as_record = AudioSegment.from_mp3(
                settings.MEDIA_ROOT +
                self.audio_file_format("mp3")
            )

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
                start_at = (start_at - offset) * 1000
            else:
                start_at = 0

            # В последней не больше, чем длинна записи
            if end_at + offset > self.duration:
                end_at = self.duration
            else:
                end_at = (end_at + offset) * 1000

            # Вырезаем кусок и сохраняем
            piece = as_record[start_at:end_at]
            piece.export(settings.MEDIA_ROOT + audio_file_path)


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

def create_account(sender, instance, **kwargs):
    """
        Создание учётки, если она не создана
    """
    try:
        instance.account
        pass
    except:
        instance.account = Account(site=settings.DOMAIN)
        instance.account.save()


# После сохранении User, создаём Account, если ещё не создан
signals.post_save.connect(create_account, sender=User)
