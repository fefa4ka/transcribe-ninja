#!/usr/bin/python
# -*- coding: utf-8 -*-

import django.db.models.signals as signals

from django.conf import settings

from django.db import models
from django.contrib.auth.models import User

from core.extra import *
from core.utils import *

import re
import subprocess

from decimal import Decimal


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


class Trash(models.Model):
    # Чтобы запись не удалялась с первого раза
    trashed_at = models.DateTimeField(blank=True, null=True)

    objects = NonTrashManager()
    trash = TrashManager()

    class Meta:
        abstract = True


class AudioFile(models.Model):
    class Meta:
        abstract = True

    def audio_file_format(self, audio_format="mp3"):
        """
            Проверяет, есть ли файл требуемого раширения
        """
        # Расчлиняем имя на имя файла и расширение
        original_file_name = self.audio_file_local()
        file_name, extension = os.path.splitext(original_file_name)

        # Имя файла в новрм формате
        file_name_format = file_name + ".%s" % audio_format

        # Если такой файл есть, то возвращаем путь к файлу
        if not os.path.isfile(settings.MEDIA_ROOT + file_name_format):
            # Если в таком формате нет, то конвертируем
            subprocess.call(
                ['ffmpeg', '-i',
                 settings.MEDIA_ROOT + original_file_name,
                 settings.MEDIA_ROOT + file_name_format])

        return file_name_format

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
        if not os.path.exists(file_path):
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


def create_account(sender, instance, **kwargs):
    """
        Создание учётки, если она не создана
    """
    try:
        instance.account
        pass
    except:
        instance.account = Account()
        instance.account.save()


# После сохранении User, создаём Account, если ещё не создан
signals.post_save.connect(create_account, sender=User)
