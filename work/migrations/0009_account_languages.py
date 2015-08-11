# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_language'),
        ('work', '0008_auto_20150729_2043'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='languages',
            field=models.ManyToManyField(to='core.Language'),
        ),
    ]
