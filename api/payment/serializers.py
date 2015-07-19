#!/usr/bin/python
# -*- coding: utf-8 -*-
from rest_framework.serializers import ModelSerializer

from work.models import Payment


class PaymentSerializer(ModelSerializer):

    class Meta:
        model = Payment
        fields = (
            "id",
            "total", "comment",
            "created")


class PaymentCreateSerializer(ModelSerializer):

    class Meta:
        model = Payment
        fields = (
            "id",
            "comment", "destination")
