#!/usr/bin/python
# -*- coding: utf-8 -*-
from rest_framework.serializers import ModelSerializer

from core.models import Feedback


class FeedbackSerializer(ModelSerializer):
    class Meta:
        model = Feedback
        fields = (
            "id",
            "email", "phone",
            "subject", "text")
