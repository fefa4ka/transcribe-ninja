# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('work', '0005_auto_20150718_1502'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.BooleanField(default=0),
        ),
        migrations.AlterField(
            model_name='price',
            name='work_type',
            field=models.IntegerField(default=0, choices=[(0, b'Transcribe audio piece'), (2, b'Read and check transcription'), (1, b'Transcription edit'), (3, b'Transcribe by SpeechKit'), (4, b'Payment')]),
        ),
    ]
