#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404

from rest_framework.response import Response

from rest_framework import viewsets

import core.async_jobs

# from core.models import *
from work.models import Queue

from serializers import *

# from api.serializers import *
from api.permissions import *
# from api.authentication import *

from datetime import datetime


class QueueViewSet(viewsets.ViewSet,
                   viewsets.GenericViewSet):
    """
        Элемент из очереди.
        Последний выданный элемент блокируется за пользователем, и по его номеру сохраняется результат.

    """
    model = Queue
    serializer_class = QueueSerializer
    permission_classes = (permissions.IsAuthenticated,
                          IsOwner,)

    # @allow_lazy_user
    def list(self, request):
        """
            Выдаёт случайный, приоритетный кусок на распознание.
            Кусок не должен содержать работу текущего пользователя.
        """

        # Сбрасываем ранее выданную очередь
        self.unlock_queue()

        # Берём задачу, связанную с кусками,
        # над который текущий пользователь не работал
        queue = self.get_queue()
        serializer = QueueSerializer(
            queue,
            context={'request': request})

        return Response(serializer.data)

    def get_queue(self):
        queues = Queue.objects.filter(priority__in=[1,2],
                                      locked__isnull=True,
                                      completed__isnull=True).order_by('?')[:10]

        for q in queues:
            # Если над какой-то из частей работал этот пользователь - ищем
            # другую часть.
            pieces = [q.piece.previous, q.piece, q.piece.next]

            for piece in pieces:
                # Каких-то кусков может не быть
                if not piece:
                    continue

                if piece.queue.filter(completed__isnull=False, owner=self.request.user).count():
                    q = None
                    break

            # Если всё ок, берём очередь в работу
            if q:
                # Блокируем очередь за пользователем
                q.locked = datetime.now()
                q.owner = self.request.user
                q.save()

                return q

        return None

    def unlock_queue(self):
        """
            Сбрасываем заблокированную очередь, если была
            Помечаем её как пропущенную, чтобы потом считать сложные
            и не востребованные куски
        """
        queue = Queue.objects.filter(
            owner=self.request.user, completed__isnull=True)

        for q in queue:
            q.locked = None
            q.owner = None
            q.skipped += 1

            q.save()

    def retrieve(self, request, pk=None):
        queryset = Queue.objects.all()
        queue = get_object_or_404(queryset, pk=pk, owner=request.user)
        serializer = QueueTranscriptionSerializer(queue)

        return Response(serializer.data)


class TranscriptionViewSet(viewsets.ModelViewSet):

    """
        Обработка данных про транскрибции.
        Список транскрибций, добавление.

    """

    model = Transcription
    queryset = Transcription.objects.all()
    serializer_class = TranscriptionQueueSerializer
    permission_classes = (permissions.IsAuthenticated,
                          IsOwner,)

    def get_queryset(self):
        """
            Выдаём список записей авторизированного пользователя
        """
        return Transcription.objects.filter(queue__owner=self.request.user)

    def create(self, request, *args, **kwargs):
        # Каждая транскрипция связанна с каким-то заказом, либо
        queue = Queue.objects.get(
            id=request.data[0]['queue'], owner=request.user)

        if queue.completed:
            return Response({'error': 'Queue already completed'}, status=status.HTTP_400_BAD_REQUEST)

        for data in request.data:
            serializer = TranscriptionQueueSerializer(data=data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            if data['queue'] != queue.id:
                return Response({'error': 'Queue should be the same'}, status=status.HTTP_400_BAD_REQUEST)

        for data in request.data:
            serializer = TranscriptionQueueSerializer(data=data)
            if serializer.is_valid():
                serializer.save()

        # Помечаем очередь как прочитанную
        queue.completed = datetime.now()
        queue.update_work_metrics()

        # TODO: Удалить аудиофайл
        queue.save()

        # Отправляем на асинхронный пересчёт зависимых кусков
        # Меняем приоритет у других кусков и перерасчёт бабла
        core.async_jobs.update_near.delay(queue)

        return Response({'done': 'ok'}, status=status.HTTP_201_CREATED)
