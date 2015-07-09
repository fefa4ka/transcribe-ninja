# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import core.utils


class Migration(migrations.Migration):

    dependencies = [
        ('transcribe', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Export',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('export_file', models.FileField(max_length=255, upload_to=core.utils.upload_export_path)),
                ('file_format', models.CharField(max_length=10)),
                ('created', models.DateTimeField(auto_now=True)),
                ('record', models.ForeignKey(related_name='exports', to='transcribe.Record')),
            ],
        ),
    ]
