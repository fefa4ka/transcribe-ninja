#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.conf import settings

from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED

from rest_framework import viewsets

import core.async_jobs

from work.models import Order, Queue
from transcribe.models import Record

from serializers import *

from api.permissions import *

from datetime import datetime, timedelta

from django.utils import timezone


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

    def get_queue(self, records_onair=settings.RECORDS_ONAIR):
        # Если слепой, выдаём задачи на транскрибирование
        records_count = Record.objects.filter(progress=3).count()
        last_record_ids = Record.objects.filter(progress=3).order_by('id').values_list('id', flat=True).distinct()[:records_onair]
        last_order_ids = Order.objects.filter(record__in=list(last_record_ids)).values_list('id', flat=True).distinct()

        if self.request.user.account.blind:
            queues = Queue.objects.filter(work_type=0,
                                          priority__in=[1,2],
                                          locked__isnull=True,
                                          order_id__in=list(last_order_ids),
                                          completed__isnull=True).exclude(owner=self.request.user).order_by('?')[:50]
        else:
            queues = Queue.objects.filter(priority__in=[1,2],
                                          locked__isnull=True,
                                          order_id__in=list(last_order_ids),
                                          completed__isnull=True).exclude(owner=self.request.user).order_by('?')[:50]

        # Если мало задач, то расширяемся
        if len(queues) < 10 and records_count > records_onair:
            return self.get_queue(records_onair + 1)

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
                q.locked = timezone.now()
                q.owner = self.request.user
                q.save()

                return q

        if records_onair == records_count:
            return None
        else:
            return self.get_queue(records_onair + 1)

    def unlock_queue(self):
        """
            Сбрасываем заблокированную очередь, если была
            Помечаем её как пропущенную, чтобы потом считать сложные
            и не востребованные куски
        """
        from itertools import chain

        queue = Queue.objects.filter(
            owner=self.request.user, completed__isnull=True)
        lastHourDateTime = datetime.today() - timedelta(hours = 1)
        queues_old = Queue.objects.filter(locked__lt=lastHourDateTime, completed__isnull=True)

        queues = list(chain(queue, queues_old))

        for q in queues:
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
        if 'queue' in request.data:
            queue_id = request.data['queue']
        elif len(request.data) > 0:
            queue_id = request.data[0]['queue']

        # Каждая транскрипция связанна с каким-то заказом, либо
        queue = Queue.objects.get(
            id=queue_id, owner=request.user)

        if queue.completed:
            return Response({'error': 'Queue already completed'}, status=HTTP_400_BAD_REQUEST)

        # Если плохая запись
        if queue_id == queue.id and 'poor' in request.data:
            queue.poored += 1

            # Если многие посчитали, что запись плохая,
            # помечаем, как выполненную
            if queue.poored > settings.SPEECH_POOR_LIMIT:
                queue.completed = timezone.now()
                queue.update_work_metrics()

            queue.save()

            core.async_jobs.update_near.delay(queue)

            return Response({'done': 'ok'}, status=HTTP_201_CREATED)

        for data in request.data:
            serializer = TranscriptionQueueSerializer(data=data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

            if data['queue'] != queue.id:
                return Response({'error': 'Queue should be the same'}, status=HTTP_400_BAD_REQUEST)

        for data in request.data:
            serializer = TranscriptionQueueSerializer(data=data)
            if serializer.is_valid():
                serializer.save()

        # Помечаем очередь как прочитанную
        queue.completed = timezone.now()
        queue.update_work_metrics()

        # TODO: Удалить аудиофайл
        queue.save()

        # Отправляем на асинхронный пересчёт зависимых кусков
        # Меняем приоритет у других кусков и перерасчёт бабла
        core.async_jobs.update_near.delay(queue)

        return Response({'done': 'ok'}, status=HTTP_201_CREATED)
