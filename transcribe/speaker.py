#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.core.files import File


class Speaker(models.Model):

    """
        Собеседники в записи

        name   - имя
        gender - пол
    """

    name = models.CharField(max_length=255)
    gender = models.CharField(max_length=1)

    def __unicode__(self):
        return "%s: %s" % (self.gender, self.name)