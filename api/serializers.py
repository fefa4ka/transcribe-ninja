#!/usr/bin/python
# -*- coding: utf-8 -*-


from django.contrib.auth.models import User


from rest_framework import serializers

from transcribe.models import *
from work.models import *


class UserSerializer(serializers.ModelSerializer):
    # records = serializers.PrimaryKeyRelatedField(many=True)
    # records = serializers.HyperlinkedRelatedField(
    #     many=True,
    #     view_name="record-detail"
    # )
    balance = serializers.ReadOnlyField(source='account.balance')

    class Meta:
        model = User
        fields = (
            "id",
            "username", "email",
            "balance",
            "records")


class TranscriptionQueueSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        many = kwargs.pop('many', True)
        super(TranscriptionQueueSerializer, self).__init__(many=many, *args, **kwargs)

    class Meta:
        model = Transcription
        fields = (
            "piece", "queue",
            "index", "text")

    def validate(self, data):
        """
        Check that the start is before the stop.
        """
        print data["queue"].locked
        if not data["queue"].locked:
            raise serializers.ValidationError("You are not in queue")

        if data["queue"].completed:
            raise serializers.ValidationError("Queue already completed")

        if not data["piece"] in data["queue"].pieces:
            raise serializers.ValidationError("Piece not in queue")

        return data

class TranscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transcription
        fields = (
            "start_at", "end_at",
            "piece", "index",
            "text", "name")

class PieceSerializer(serializers.ModelSerializer):
    transcriptions = TranscriptionSerializer(many=True)

    class Meta:
        model = Piece
        fields = (
            "id",
            "start_at", "end_at", "duration",
            "speaker",
            "transcriptions")


class RecordSerializer(serializers.ModelSerializer):

    class Meta:
        model = Record
        fields = (
            "id",
            "title", "audio_file",
            "duration",
            "completed", "progress")


class RecordDetailSerializer(serializers.ModelSerializer):
    transcriptions = TranscriptionSerializer(many=True)
    class Meta:
        model = Record
        fields = (
            "id",
            "title", "audio_file",
            "duration",
            "completed", "progress",
            "transcriptions")

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = (
            "id", "record",
            "start_at", "end_at")


class QueueSerializer(serializers.ModelSerializer):
    pieces = PieceSerializer(many=True)
    price = serializers.SlugRelatedField(
        read_only=True,
        slug_field='price')

    class Meta:
        model = Queue
        fields = (
            "id", "audio_file",
            "work_type", "price", "total_price",
            "offset_parts",
            "pieces")
