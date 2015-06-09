#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.core.files import File

import os
import time
import shutil

import urllib2

from xml.dom.minidom import parseString as XMLParse

from datetime import datetime

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

    # По умолчанию показывать только последнии трансприпции
    # Отдавать транскрипции, время выполнении очереди у которой последний.
    @property
    def transcriptions(self):
        last_completed= self.all_transcriptions.order_by('-queue__completed').first()
        if last_completed:
            return self.all_transcriptions.filter(queue=last_completed.queue).order_by('index')
        else:
            return Transcription.objects.none()

    def __unicode__(self):
        return "%d-%d sec" % (self.start_at, self.end_at)

    @property
    def previous(self):
        """
            Предыдущий кусок
        """

        piece = Piece.objects.filter(
            record=self.record,
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
            record=self.record,
            start_at__gte=self.end_at).order_by('start_at')

        if not piece:
            return None

        return piece[0]

    @property
    def letters_per_sec(self):
        return self.duration / \
            np.sum([len(t.text) for t in self.transcriptions.all()])

    @property
    def transcribe_queue(self):
        return self.queue.filter(work_type=0)[0]

    @property
    def check_transcription_queue(self):
        return self.queue.filter(work_type=1)[0]

    def recognize(self, as_record=None):
        """
            Распознаём через бота Google Speech API
        """
        transcribe_queue = self.transcribe_queue

        # Ничего не делаем, если это вычитка
        if transcribe_queue.completed:
            return

        transcribe_queue.owner = User.objects.get(username="speech_bot")
        transcribe_queue.locked = datetime.now()

        transcribe_queue.save()

        # Генерим вав файл с одним каналом звука
        # wav = self.audio_file_format('wav', 1)
        wav = self.record.cut_to_file(
            file_name=upload_piece_path(self, extension="wav"),
            start_at=self.start_at,
            end_at=self.end_at,
            as_record=as_record,
            offset=0,
            channels=1
        )

        transcribe = self._recognize_yandex(wav)

        if not transcribe:
            transcribe_queue.owner = None
            transcribe_queue.locked = None
            transcribe_queue.save()

            return False

        for index, word in enumerate(transcribe):
            if isinstance(word, list):
                # TODO: Для интерфейса, где можно будет выбирать предположения
                # transcribe[index] = "(%s)" % "|".join(word)
                transcribe[index] = word[0]
            else:
                transcribe[index] = word

        # Добавляем транскрибцию найденную
        # recognize speech using Google Speech Recognition
        transcription = Transcription(
            queue=self.transcribe_queue,
            piece=self,
            text=" ".join(transcribe)
        )

        transcription.save()

        transcribe_queue.completed = datetime.now()
        transcribe_queue.save()

        transcribe_queue.update_priority()

    def _recognize_google(self, wav_file_path):
        import speech_recognition as sr
        # TODO: Локализация
        r = sr.Recognizer(language='ru-RU', key=settings.GOOGLE_API_KEY)

        # use wav file as the audio source
        with sr.WavFile(str(settings.MEDIA_ROOT + wav_file_path)) as source:
            # extract audio data from the file
            audio = r.record(source)

        try:
            transcribe_queue = self.transcribe_queue
            # Добавляем транскрибцию найденную
            # recognize speech using Google Speech Recognition
            transcription = Transcription(
                queue=self.transcribe_queue,
                piece=self,
                text=r.recognize(audio)
            )

            transcription.save()

            transcribe_queue.completed = datetime.now()
            transcribe_queue.save()

            transcribe_queue.update_priority()

            # TODO: удалять файл

            print("Transcription: " + r.recognize(audio))
        # speech is unintelligible
        except LookupError:
            print("Could not understand audio")

    def _recognize_yandex(self, wav_file_path):
        from difflib import SequenceMatcher
        # Отправляем яндексу
        url = "https://asr.yandex.net/asr_xml?key=%s&uuid=%s&topic=notes&lang=ru-RU" % (settings.YANDEX_API_KEY, settings.UUID)
        length = os.path.getsize(settings.MEDIA_ROOT + wav_file_path)
        file_data = open(settings.MEDIA_ROOT + wav_file_path, 'rb')

        request = urllib2.Request(url, data=file_data)
        request.add_header('Content-Length', '%d' % length)
        request.add_header('Content-Type', 'audio/x-wav')


        try:
            result = XMLParse(urllib2.urlopen(request).read().strip())
        except:
            print "Can't send request to Yandex.SpeechKit: %s" % wav_file_path

            return False

        variants = []
        for variant in result.getElementsByTagName('variant'):
            variants.append(variant.childNodes[0].nodeValue)

        # Берём главный результат и ищем для каждого слова альтернативу
        if len(variants) >= 1:
            transcribe = []
            main_variant = variants.pop(0)
            for word_index, word in enumerate(main_variant.split(" ")):
                result_word = [word]
                for index, variant in enumerate(variants):
                    variant = variant.split(" ")
                    try:
                        diff = SequenceMatcher(None, word, variant[word_index])
                        ratio = diff.ratio()
                        # Если слово очень похоже, то добавляем как альтернативу
                        if ratio > 0.65 and ratio != 1:
                            result_word.append(variant[word_index])
                    except IndexError:
                        pass

                    # TODO: Что делать с теми случаями, когда какое-то слово пропускается?

                if len(result_word) > 1:
                    transcribe.append(result_word)
                else:
                    transcribe.append(word)

            return transcribe

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

    piece = models.ForeignKey(Piece, related_name='all_transcriptions')
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
        return self.start_at + len(self.text) * self.piece.letters_per_sec

    @property
    def name(self):
        if self.speaker:
            speaker = self.speaker
        else:
            speaker = self.piece.speaker

        # print speaker
        # # Если нет имени
        # # Проверяем, входит ли в основной набор собеседников
        # if not speaker.name:
        #     # Если да, и собеседников двое
        #     # то имена «Женщина» или «Мужчина»
        #     name = "Female" if speaker.gender == "F" else "Male"

        return speaker.name

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
