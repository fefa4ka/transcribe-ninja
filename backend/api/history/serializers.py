#!/usr/bin/python
# -*- coding: utf-8 -*-
from rest_framework.serializers import ModelSerializer

from work.models import Queue


class HistorySerializer(ModelSerializer):

    class Meta:
        model = Queue
        fields = (
            "id",
            "work_type", "duration",
            "work_length", "total_price",
            "mistakes_length", "completed", "checked")
