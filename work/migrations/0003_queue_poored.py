# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('work', '0002_remove_account_balance'),
    ]

    operations = [
        migrations.AddField(
            model_name='queue',
            name='poored',
            field=models.IntegerField(default=0),
        ),
    ]
