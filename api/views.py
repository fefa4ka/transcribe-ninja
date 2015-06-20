#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.shortcuts import get_object_or_404

import django_filters

from rest_framework import generics
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import status
from rest_framework import filters
from rest_framework import pagination

from rest_framework.views import APIView
from rest_framework.response import Response

# import rest_framework_bulk.mixins

import core.async_jobs

from core.models import *

from api.serializers import *
from api.permissions import *
from api.authentication import *

from datetime import datetime

from itertools import chain

# from lazysignup.decorators import allow_lazy_user

class AuthView(APIView):

    """
        Класс аутентификации.
        post    - залогиниться
        delete  - разлогиниться
    """
    authentication_classes = (QuietBasicAuthentication,)

    def post(self, request, *args, **kwargs):
        login(request, request.user)

        return Response(
            UserSerializer(
                request.user,
                context={'request': request}
            ).data)

    def delete(self, request, *args, **kwargs):
        logout(request)

        return Response({})


class CurrentUserView(APIView):

    """
        Информация о текущем пользователе
    """
    queryset = User

    def get(self, request):
        # Если не залогинен, то отдаё пустой ответ
        if not request.user.id:
            return Response({})

        serializer = UserSerializer(
            request.user,
            context={'request': request})
        return Response(serializer.data)


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


class PieceViewSet(generics.ListAPIView):
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


class RecordTranscription(generics.GenericAPIView):

    """
        Список транскрибций для записи
        TODO: сделать
    """
    queryset = Record.objects.all()
    # renderer_classes = (renderers.StaticHTMLRenderer,)

    def get(self, request, *args, **kwargs):
        record = self.get_object()
        return Response(record.title)


class OrderViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):

    """
        Заказ на транскрибцию
    """
    model = Order
    serializer_class = OrderSerializer
    permission_classes = (permissions.IsAuthenticated,
                          IsOwner,)

    def create(self, request):
        """
            Создание заказа
        """
        serializer = OrderSerializer(data=request.data)

        if serializer.is_valid():
            # Продолжительность записи не может быть меньше нуля или равно ему
            duration = float(
                request.data['end_at']) - float(request.data['start_at'])

            # TODO: разрешить стенографировать только свои записи

            if duration > 0:
                # Загружем цену за стенографирование
                object_id = ContentType.objects.get_for_model(Order).id
                price = Price.objects.filter(
                    content_type_id=object_id,
                    default=1
                )[0]

                # Считаем общую цену.
                # Прайс за минуту, поэтому продолжительность делим на 60
                total = price.price * duration / 60

                # Если денег на балансе достаточно, создаём заказ
                if request.user.account.balance >= total:
                    # Сохраняем заказ для определённого пользователя
                    obj = serializer.save(owner=request.user, price=price)

                    # Создаём очередь, чтобы работать с записью
                    core.async_jobs.make_queue.delay(obj)

                    # Если всё хорошо, отправляем информацию о созданном заказе
                    return Response(serializer.data)
                else:
                    errors = [{'balance': 'Not enought money.'}]

            else:
                errors = [{'end_at': 'End_at should be greater that start_at'}]

        else:
            errors = serializer.errors

        return Response(
            errors,
            status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        """
            Список заказов для текущего пользователя
        """
        return Order.objects.filter(owner=self.request.user)


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


class HistoryFilter(django_filters.FilterSet):
    class Meta:
        model = Queue
        fields = [ 'id', 'completed', 'checked' ]


class StandartResultSetPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class HistoryViewSet(generics.ListAPIView):
    """
        Список кусков записи
    """
    model = Queue
    serializer_class = HistorySerializer
    permission_classes = (permissions.IsAuthenticated,
                          IsOwner,)
    pagination_class = StandartResultSetPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = HistoryFilter

    def get_queryset(self):
        user = self.request.user
        if 'checked' in self.request.QUERY_PARAMS:
            return user.account.queues(unchecked=False).order_by('-checked')
        elif 'unchecked' in self.request.QUERY_PARAMS:
            return user.account.queues(unchecked=True).order_by('-completed')

        return user.queue.filter(completed__isnull=False)

class StatisticsView(APIView):
    permission_classes = (permissions.IsAuthenticated,
                          IsOwner,)

    def get(self, request, *args, **kwargs):
        after_date = request.query_params.get('after_date', None)
        account = request.user.account
        statistics = {
            "work_length": 0,
            "mistakes_length": 0,
            "checked_length": 0,
            "duration_transcribe": 0,
            "duration_check": 0
        }
        queues = None

    # try:

        if 'unchecked' in self.request.QUERY_PARAMS:
            queues = account.queues(unchecked=True, after_date=after_date).order_by('-completed')

        if 'checked' in self.request.QUERY_PARAMS:
            queues = account.queues(unchecked=False, after_date=after_date).order_by('-checked')

        if not queues:
            if after_date:
                queues = request.user.queue.filter(completed__gt=after_date)
            else:
                queues = request.user.queue.filter(completed__isnull=False)

            checked_queues = account.queues(unchecked=False, after_date=after_date).order_by('-checked')
            for queue in checked_queues:
                statistics["checked_length"] += queue.work_length - queue.mistakes_length

        for queue in queues:
            statistics["work_length"] += queue.work_length
            statistics["mistakes_length"] += queue.mistakes_length


            if queue.work_type == Queue.TRANSCRIBE:
                statistics["duration_transcribe"] += queue.duration
            elif queue.work_type == Queue.EDIT:
                statistics["duration_check"] += queue.duration

        return Response(statistics)
        # except:
        #     return Response({"success": False})


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
            serializer = self.get_serializer(data=data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            if data['queue'] != queue.id:
                return Response({'error': 'Queue should be the same'}, status=status.HTTP_400_BAD_REQUEST)

        for data in request.data:
            serializer = self.get_serializer(data=data)
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
