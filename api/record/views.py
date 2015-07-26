#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404

from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.generics import ListAPIView
from rest_framework.status import HTTP_400_BAD_REQUEST

from rest_framework.response import Response

import core.async_jobs

from transcribe.models import Record

from serializers import *

from api.permissions import *

import logging

logger = logging.getLogger(__name__)


class RecordViewSet(mixins.ListModelMixin,
                    mixins.DestroyModelMixin,
                    GenericViewSet):
    """
        Обработка данных про записи.
        Список записей, Просмотр, Удаление.

    """
    queryset = Record.objects.all()
    serializer_class = RecordSerializer
    permission_classes = (permissions.IsAuthenticated,
                          IsOwner,)

    def get_queryset(self):
        """
            Выдаём список записей авторизированного пользователя
        """
        return Record.objects.filter(owner=self.request.user)

    def create(self, request):
        """
            Загрузка и создание записи
        """
        serializer = RecordSerializer(data=request.data)

        if serializer.is_valid():
            # Помечаем, какой пользователь создал запись
            obj = serializer.save(owner=request.user)

            # Отправляем на асинхронную подготовку
            core.async_jobs.record_prepare.delay(obj)

            return Response(serializer.data)

        logger.error("Record tried to create with errors: %s\n%s" % (serializer.errors, request.__dict__))
        
        # Если плохие данные, выдаём ошибку
        return Response(
            serializer.errors,
            status=HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        queryset = Record.objects.filter(owner=request.user)
        record = get_object_or_404(queryset, pk=pk)
        serializer = RecordDetailSerializer(record)

        return Response(serializer.data)


class PieceViewSet(ListAPIView):
    """
        Список кусков записи
    """
    model = Piece
    serializer_class = PieceSerializer
    permission_classes = (permissions.IsAuthenticated,
                          IsOwner,)

    def get_queryset(self):
        """
            Список кусков, только для конкретной записи record_id
        """
        record_id = self.kwargs['record_id']
        return Piece.objects.filter(record_id=record_id)

