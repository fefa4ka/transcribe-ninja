# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import core.utils
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('transcribe', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('trashed_at', models.DateTimeField(null=True, blank=True)),
                ('start_at', models.FloatField()),
                ('end_at', models.FloatField()),
                ('created', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(related_name='user-orders', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('total', models.FloatField()),
                ('status', models.IntegerField(default=0)),
                ('created', models.DateTimeField(auto_now=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('owner', models.ForeignKey(related_name='user-payments', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Price',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('work_type', models.IntegerField(default=0, choices=[(0, b'Transcribe audio piece'), (1, b'Read and check transcription'), (2, b'Transcription edit')])),
                ('price', models.FloatField()),
                ('default', models.BooleanField(default=False)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Queue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('audio_file', models.FileField(max_length=255, upload_to=core.utils.upload_queue_path)),
                ('work_type', models.IntegerField(default=0, choices=[(0, b'Transcribe'), (1, b'Check and edit')])),
                ('priority', models.BooleanField(default=False)),
                ('locked', models.DateTimeField(null=True)),
                ('skipped', models.IntegerField(default=0)),
                ('completed', models.DateTimeField(null=True)),
                ('order', models.ForeignKey(related_name='queue', to='work.Order')),
                ('owner', models.ForeignKey(related_name='queue', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('piece', models.ForeignKey(related_name='queue', to='transcribe.Piece')),
                ('price', models.ForeignKey(to='work.Price')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='payment',
            name='price',
            field=models.ForeignKey(to='work.Price'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='price',
            field=models.ForeignKey(to='work.Price'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='record',
            field=models.ForeignKey(to='transcribe.Record'),
            preserve_default=True,
        ),
    ]
