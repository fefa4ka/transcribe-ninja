# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('work', '0003_queue_poored'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='comment',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]
