# !/usr/bin/python
# -*- coding: utf-8 -*-
from django.conf import settings

import os

import time

import xlsxwriter

from hashlib import md5


class ExportXLS:
    def _to_xls(self, transcriptions):
        file_name = md5(
            str(time.time())
        ).hexdigest()
        xls_file_path = os.path.join(settings.TEMP_DIR, "%s.xls" % file_name)

        # Create an new Excel file and add a transcriptions_sheet.
        workbook = xlsxwriter.Workbook(xls_file_path)
        transcriptions_sheet = workbook.add_worksheet("Transcription")

        # Widen the first column to make the text clearer.
        transcriptions_sheet.set_column('A:A', 9)
        transcriptions_sheet.set_column('B:B', 9)
        transcriptions_sheet.set_column('C:C', 15)
        transcriptions_sheet.set_column('D:D', 100)

        # Add a bold format to use to highlight cells.
        bold = workbook.add_format({
            'bold': True,
            'font_name': 'Cambria',
            'font_size': 14
        })

        text = workbook.add_format({
            'text_wrap': True,
            'font_name': 'Cambria',
            'valign': 'top',
            'font_size': 12
        })

        transcriptions_sheet.insert_image('A1', 'core/media/logos/stenographus.png')
        transcriptions_sheet.set_row(0, 50)

        # Write some simple text.
        transcriptions_sheet.write('A2', u'Стенограмма записи «%s»' % self.record.title, bold)

        transcriptions_sheet.write('A3', u'Начало', bold)
        transcriptions_sheet.write('B3', u'Конец', bold)
        transcriptions_sheet.write('C3', u'Собеседник', bold)
        transcriptions_sheet.write('D3', u'Текст', bold)

        for index, transcription in enumerate(transcriptions):
            start_at = time.strftime(
                "%H:%M:%S",
                time.gmtime(transcription.start_at)
            )
            end_at = time.strftime(
                u"%H:%M:%S",
                time.gmtime(transcription.end_at)
            )

            # TODO: Локализация
            speaker_gender, speaker_index = u"Женщина" if transcription.speaker_code[0] == "F"\
                                            else u"Мужчина",\
                                            transcription.speaker_code[1]

            # Speaker
            transcriptions_sheet.write(index + 3, 0, start_at, text)
            transcriptions_sheet.write(index + 3, 1, end_at, text)
            transcriptions_sheet.write(index + 3, 2, u"%s %s" % (speaker_gender, speaker_index), text)
            transcriptions_sheet.write(index + 3, 3, u"%s" % transcription.text_pretty, text)

        workbook.close()

        return xls_file_path
