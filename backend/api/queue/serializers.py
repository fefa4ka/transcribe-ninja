#!/usr/bin/python
# -*- coding: utf-8 -*-
from rest_framework import serializers

from transcribe.models import Transcription
from work.models import Queue

from api.record.serializers import PieceSerializer


class TranscriptionQueueSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        many = kwargs.pop('many', True)
        super(TranscriptionQueueSerializer, self).__init__(many=many, *args, **kwargs)

    class Meta:
        model = Transcription
        fields = (
            "piece", "queue",
            "index", "text_pretty", "speaker_code")

    def validate(self, data):
        if not data["queue"].locked:
            raise serializers.ValidationError("You are not in queue")

        if data["queue"].completed:
            raise serializers.ValidationError("Queue already completed")

        if not data["piece"] in data["queue"].pieces:
            raise serializers.ValidationError("Piece not in queue")

        return data


class QueueTranscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Queue
        fields = (
            "id", "original_transcription",
            "transcription", "checked_transcription")


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
