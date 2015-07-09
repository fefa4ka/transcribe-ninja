#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.conf import settings

import os

import time

import codecs

from hashlib import md5


class ExportTXT:
    def _to_txt(self, transcriptions):
        file_name = md5(
            str(time.time())
        ).hexdigest()
        txt_file_path = os.path.join(settings.TEMP_DIR, "%s.txt" % file_name)

        with codecs.open(txt_file_path, 'w+', 'utf-8') as txt_file:
            for index, transcription in enumerate(transcriptions):
                start_at = time.strftime(
                    u"%H:%M:%S",
                    time.gmtime(transcription.start_at)
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
                    u"%s" % (start_at),
                    u"\n".join(text)
                ]

                txt_file.write("\n".join(record) + "\n\n")

        return txt_file_path
