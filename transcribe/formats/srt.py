#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.conf import settings

import os

import time

import codecs

from hashlib import md5


class ExportSRT:
    def _to_srt(self, transcriptions):
        file_name = md5(
            str(time.time())
        ).hexdigest()
        srt_file_path = os.path.join(settings.TEMP_DIR, "%s.srt" % file_name)

        with codecs.open(srt_file_path, 'w+', 'utf-8') as srt_file:
            for index, transcription in enumerate(transcriptions):
                start_at = time.strftime(
                    u"%H:%M:%S,000",
                    time.gmtime(transcription.start_at)
                )
                end_at = time.strftime(
                    u"%H:%M:%S,000",
                    time.gmtime(transcription.end_at)
                )

                # TODO: Локализация
                speaker_gender, speaker_index = u"Женщина" if transcription.speaker_code[0] == "F"\
                                                else u"Мужчина",\
                                                transcription.speaker_code[1]

                text = [
                    u"%s %s" % (speaker_gender, speaker_index),
                    transcription.text_pretty
                ]

                record = [
                    str(index),
                    u"%s --> %s" % (start_at, end_at),
                    u": ".join(text)
                ]

                srt_file.write("\n".join(record) + "\n\n")

        return srt_file_path
