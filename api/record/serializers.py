#!/usr/bin/python
# -*- coding: utf-8 -*-
from rest_framework import serializers

from transcribe.models import Record, Piece, Transcription, Export


class TranscriptionSerializer(serializers.ModelSerializer):
    total_price = serializers.ReadOnlyField(source='queue.total_price')

    class Meta:
        model = Transcription
        fields = (
            "start_at", "end_at",
            "piece", "index",
            "text", "speaker_code", "gender",
            "total_price")


class PieceSerializer(serializers.ModelSerializer):
    transcriptions = TranscriptionSerializer(many=True)
    speaker = serializers.ReadOnlyField(source='speaker.gender')

    class Meta:
        model = Piece
        fields = (
            "id",
            "start_at", "end_at", "duration",
            "speaker",
            "transcriptions")


class ExportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Export
        fields = (
            "export_file", "file_format")


class RecordSerializer(serializers.ModelSerializer):
    exports = ExportSerializer(many=True)

    class Meta:
        model = Record
        fields = (
            "id",
            "title", "audio_file",
            "duration", "speakers",
            "completed", "progress", "order", "exports")


class RecordDetailSerializer(serializers.ModelSerializer):
    transcriptions = TranscriptionSerializer(many=True)

    class Meta:
        model = Record
        fields = (
            "id",
            "title", "audio_file",
            "duration",
            "completed", "progress",
            "transcriptions", "order")
