#!/usr/bin/python
# -*- coding: utf-8 -*-
from rest_framework import serializers

from transcribe.models import *
from work.models import *


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = (
            "id", "record",
            "start_at", "end_at")
