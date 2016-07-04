# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('work', '0009_account_languages'),
    ]

    operations = [
        migrations.AlterField(
            model_name='queue',
            name='work_type',
            field=models.IntegerField(default=0, choices=[(0, b'Transcribe'), (1, b'Check and edit'), (2, b'Pretty checked text'), (3, b'Check pretty text')]),
        ),
    ]
