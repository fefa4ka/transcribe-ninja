#!/usr/bin/python
# -*- coding: utf-8 -*-


from django.contrib.auth.models import User


from rest_framework import serializers

from backend.transcribe.models import *
from backend.order.models import *


class UserSerializer(serializers.ModelSerializer):
    # records = serializers.PrimaryKeyRelatedField(many=True)
    # records = serializers.HyperlinkedRelatedField(
    #     many=True,
    #     view_name="record-detail"
    # )
    balance = serializers.ReadOnlyField(source='account.balance')

    class Meta:
        model = User
        fields = ("id", "username", "email", "balance", "records")


class RecordSerializer(serializers.ModelSerializer):
    completed = serializers.ReadOnlyField(source='completed_percentage')

    class Meta:
        model = Record
        fields = ("id", "title", "file_name", "duration", "completed", "progress")

    def file_name_mp3(self, obj):
        return obj.file_name_format('mp3')


class PieceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Piece
        fields = ("id", "start_at", "end_at", "duration", "speaker")


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("id", "record", "start_at", "end_at")
