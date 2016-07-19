#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings

import os

import urllib2

from xml.dom.minidom import parseString as XMLParse

from django.utils import timezone

import numpy as np

from record import Record

from speaker import Speaker

from core.utils import *
from core.models import *
from core.extra import *


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
    speaker = models.ForeignKey(Speaker, blank=True, null=True, related_name='pieces')

    @property
    def transcriptions(self):
        from .models import Transcription
        from work.models import Queue
        # Смотрим какие очереди выполненны
        # последними и от них выдаём транскрибцию.
        queues = [self.transcribe_queue, self.check_transcription_queue, self.previous_check_transcription_queue]
        queues_ids = [q.id for q in queues]

        last_queue = Queue.objects.filter(id__in=queues_ids, completed__isnull=False).order_by('-completed')[:1]
        # if self.previous:
        #     previous_check_queue = self.previous.check_transcription_queue

        # if self.previous and previous_check_queue.completed\
        #     and self.check_transcription_queue.completed\
        #     and previous_check_queue.completed > self.check_transcription_queue.completed:
        #     queue_id = previous_check_queue.id
        # else:
        #     # По умолчанию показывать только последнии трансприпции
        #     # Отдавать транскрипции,
        #     # время выполнении очереди у которой последний.
        #     if self.check_transcription_queue.completed:
        #         queue_id = self.check_transcription_queue.id
        #     else:
        #         queue_id = self.transcribe_queue.id

        if len(last_queue) > 0:
            return self.all_transcriptions.\
                filter(queue_id=last_queue[0]).order_by('index')
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
        # х3 почему их может не быть
        try:
            return self.queue.filter(work_type=0)[0]
        except:
            return None

    @property
    def check_transcription_queue(self):
        try:
            return self.queue.filter(work_type=1)[0]
        except:
            return None

    @property
    def previous_check_transcription_queue(self):
        if self.previous:
            return self.previous.check_transcription_queue
        else:
            return self.check_transcription_queue

    @property
    def recognize_status(self):
        status = 0
        if self.transcribe_queue and self.transcribe_queue.completed:
            status += 1
        if self.previous_check_transcription_queue and self.previous_check_transcription_queue.completed:
            status += 1
        if self.check_transcription_queue and self.check_transcription_queue.completed:
            status += 1

        return status

    def recognize(self):
        """
            Распознаём через бота Google Speech API
        """
        transcribe_queue = self.transcribe_queue

        # Ничего не делаем, если это вычитка
        if transcribe_queue.locked or transcribe_queue.completed:
            return

        transcribe_queue.owner = User.objects.get(username="speech_bot")
        transcribe_queue.locked = timezone.now()

        transcribe_queue.save()

        # Генерим вав файл с одним каналом звука
        # wav = self.audio_file_format('wav', 1)
        wav = self.record.cut_to_file(
            file_name=upload_piece_path(self, extension="wav"),
            start_at=self.start_at,
            end_at=self.end_at,
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

        transcribe_queue.completed = timezone.now()
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

            transcribe_queue.completed = timezone.now()
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
        url = "https://asr.yandex.net/asr_xml?\
            key=%s\
            &uuid=%s\
            &topic=notes\
            &lang=ru-RU" % (settings.YANDEX_API_KEY, settings.UUID)
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
