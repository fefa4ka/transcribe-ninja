# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import core.utils
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('work', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Logs',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('play_log', models.TextField()),
                ('key_log', models.TextField()),
                ('mouse_log', models.TextField()),
                ('start_at', models.DateTimeField()),
                ('end_at', models.DateTimeField(auto_now=True)),
                ('platform', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Piece',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_at', models.FloatField()),
                ('end_at', models.FloatField()),
                ('duration', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('trashed_at', models.DateTimeField(null=True, blank=True)),
                ('title', models.CharField(max_length=200)),
                ('audio_file', models.FileField(max_length=255, upload_to=core.utils.upload_record_path)),
                ('duration', models.FloatField(default=0)),
                ('speakers', models.IntegerField(default=2)),
                ('language', models.CharField(default=b'ru-RU', max_length=20)),
                ('progress', models.IntegerField(default=0, choices=[(0, b'Uploaded'), (2, b'Ordered'), (1, b'Diarized'), (3, b'Recognizing'), (4, b'Completed')])),
                ('created', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(related_name='records', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Speaker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('gender', models.CharField(max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='Transcription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('index', models.IntegerField(default=0)),
                ('text', models.TextField()),
                ('work_type', models.IntegerField(default=0)),
                ('speaker_code', models.CharField(max_length=2)),
                ('piece', models.ForeignKey(related_name='all_transcriptions', to='transcribe.Piece')),
                ('queue', models.ForeignKey(related_name='transcriptions', to='work.Queue')),
                ('speaker', models.ForeignKey(related_name='transcriptions', to='transcribe.Speaker')),
            ],
        ),
        migrations.AddField(
            model_name='piece',
            name='record',
            field=models.ForeignKey(related_name='pieces', to='transcribe.Record'),
        ),
        migrations.AddField(
            model_name='piece',
            name='speaker',
            field=models.ForeignKey(blank=True, to='transcribe.Speaker', null=True),
        ),
        migrations.AddField(
            model_name='logs',
            name='transcription',
            field=models.ForeignKey(to='transcribe.Transcription'),
        )
    ]
