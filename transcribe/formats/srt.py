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

                record = [
                    str(index),
                    u"%s --> %s" % (start_at, end_at),
                    transcription.text_pretty
                ]

                srt_file.write("\n".join(record) + "\n\n")

        return srt_file_path
