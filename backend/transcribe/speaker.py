#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db import models


class Speaker(models.Model):

    """
        Организация в которой

        name   - имя
        gender - пол
    """

    name = models.CharField(max_length=255)
    gender = models.CharField(max_length=1)

    def __unicode__(self):
        return "%s: %s" % (self.gender, self.name)
