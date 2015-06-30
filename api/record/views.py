#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404


from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import status

from rest_framework.response import Response

import core.async_jobs

from core.models import *

from api.serializers import *
from api.permissions import *
from api.authentication import *


class RecordViewSet(mixins.ListModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
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

        # Если плохие данные, выдаём ошибку
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        queryset = Record.objects.all()
        record = get_object_or_404(queryset, pk=pk)
        serializer = RecordDetailSerializer(record)

        return Response(serializer.data)
