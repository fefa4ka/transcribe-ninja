# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('work', '0007_account_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='editing',
            field=models.BooleanField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='speedup',
            field=models.BooleanField(default=0),
            preserve_default=False,
        ),
    ]
