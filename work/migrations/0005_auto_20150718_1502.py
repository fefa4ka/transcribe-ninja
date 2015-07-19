# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('work', '0004_payment_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='destination',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='payment',
            name='owner',
            field=models.ForeignKey(related_name='payments', to=settings.AUTH_USER_MODEL),
        ),
    ]
