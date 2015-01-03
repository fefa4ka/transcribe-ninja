# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import core.utils
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('work', '0001_initial'),
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
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Piece',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_at', models.FloatField()),
                ('end_at', models.FloatField()),
                ('duration', models.FloatField()),
            ],
            options={
            },
            bases=(models.Model,),
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
                ('progress', models.IntegerField(default=0, choices=[(0, b'Uploaded'), (1, b'In progress'), (2, b'Completed')])),
                ('created', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(related_name='records', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Speaker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('gender', models.CharField(max_length=1)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Transcription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('index', models.IntegerField(default=0)),
                ('text', models.TextField()),
                ('work_type', models.IntegerField(default=0)),
                ('speaker', models.IntegerField(default=0)),
                ('piece', models.ForeignKey(to='transcribe.Piece')),
                ('queue', models.ForeignKey(related_name='transcriptions', to='work.Queue')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='piece',
            name='record',
            field=models.ForeignKey(related_name='pieces', to='transcribe.Record'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='piece',
            name='speaker',
            field=models.ForeignKey(blank=True, to='transcribe.Speaker', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='logs',
            name='transcription',
            field=models.ForeignKey(to='transcribe.Transcription'),
            preserve_default=True,
        ),
    ]
