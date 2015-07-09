#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db import models
# from django.conf import settings
from django.core.files import File

import os
import shutil

from core.utils import upload_export_path

from transcribe.models import Record

import formats

class Export(models.Model):
    record = models.ForeignKey(Record, related_name='exports')
    export_file = models.FileField(
        max_length=255,
        upload_to=upload_export_path)
    file_format = models.CharField(max_length=10)
    created = models.DateTimeField(auto_now=True)

    def generate_file(self):
        pass
        # formats.ExportSRT, formats.ExportTXT, formats.ExportXLS
        # export_file = getattr(self, "_to_" + self.file_format)(self.record.transcriptions)

        # # Закачиваем на амазон
        # self.export_file.save(
        #     export_file,
        #     File(
        #         open(export_file)
        #     )
        # )

        # # Удаляем временный файл
        # shutil.rmtree(
        #     export_file,
        #     ignore_errors=True)
