# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('work', '0006_auto_20150724_0128'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='price',
            field=models.ForeignKey(default=1, to='work.Price'),
            preserve_default=False,
        ),
    ]
