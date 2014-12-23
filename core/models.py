#!/usr/bin/python
# -*- coding: utf-8 -*-

import django.db.models.signals as signals

from django.db import models
from django.contrib.auth.models import User


class Account(models.Model):
    """
        Расширенная информация по учётной записи

        user    - пользователь

        phone   - номер телефона

        raing   - рейтинг

        balance - баланс
    """

    user = models.OneToOneField(User)

    phone = models.CharField(max_length=50)

    rating = models.FloatField(default=0)
    balance = models.FloatField(default=0)


def create_account(sender, instance, **kwargs):
    """
        Создание учётки, если она не создана
    """
    try:
        instance.account
        pass
    except:
        instance.account = Account()
        instance.account.save()


# После сохранении User, создаём Account, если ещё не создан
signals.post_save.connect(create_account, sender=User)
