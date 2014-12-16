#!/usr/bin/python
# -*- coding: utf-8 -*-

import django.db.models.signals as signals

from django.db import models
from django.contrib.auth.models import User


class Account(models.Model):
    user = models.OneToOneField(User)

    phone = models.CharField(max_length=50)

    rating = models.FloatField(default=0)
    balance = models.FloatField(default=0)


def create_account(sender, instance, **kwargs):
    try:
        instance.account
        pass
    except RelatedObjectDoesNotExist:
        instance.account = Account()
        instance.account.save()


# register the signal
signals.post_save.connect(create_account, sender=User)