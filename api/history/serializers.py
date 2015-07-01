#!/usr/bin/python
# -*- coding: utf-8 -*-
from rest_framework import serializers

from transcribe.models import *
from work.models import *


class HistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Queue
        fields = (
            "id",
            "work_type", "duration",
            "work_length",
            "mistakes_length", "completed", "checked")
