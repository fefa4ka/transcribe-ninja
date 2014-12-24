#!/usr/bin/python
# -*- coding: utf-8 -*-

import django.db.models.signals as signals

from django.db import models
from django.contrib.auth.models import User

from core.extra import *
from core.utils import *

class Account(models.Model):
    """
        Расширенная информация по учётной записи

        user    - пользователь

        phone   - номер телефона

        raing   - рейтинг

        balance - баланс
    """

    user = models.OneToOneField(User)

    phone = models.CharField(max_length=50)

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
    audio_file = ContentTypeRestrictedFileField(
        max_length=255,
        upload_to=upload_record_path,
        content_types=["audio/mpeg", "audio/vnd.wav"],
        max_upload_size=429916160)

    class Meta:
        abstract = True

    def audio_file_format(self, audio_format="mp3"):
        """
            Проверяет, есть ли файл требуемого раширения
        """
        # Расчлиняем имя на имя файла и расширение
        original_file_name = self.audio_file_local()
        file_name, extension = os.path.splitext()

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
        s3_record_file = self.audio_file
        record_file_name = str(s3_record_file)

        file_path = settings.MEDIA_ROOT + record_file_name

        # Если файл есть, ничего не делаем, возращаем путь до него
        if os.path.isfile(file_path):
            return file_path

        # Если папок нет - создаём
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path))

        # Скачиваем мп3
        s3_record_file.open()
        mp3_data = s3_record_file.read()

        # Сохраняем в файл
        mp3_file = open(
            file_path,
            'w+')
        mp3_file.write(mp3_data)
        mp3_file.close()

        return file_path

    def audio_file_length(self):
        """
            Узнаём длину записи в секундах с помощью ffmpeg
        """
        path = settings.MEDIA_ROOT + self.audio_file_format('wav')

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
