#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User


class Account(models.Model):
    user = models.OneToOneField(User)

    phone = models.CharField(max_length=50)
    balance = models.FloatField()
