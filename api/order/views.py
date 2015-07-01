#!/usr/bin/python
# -*- coding: utf-8 -*-
from rest_framework.response import Response
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

import core.async_jobs

from serializers import *

from api.permissions import *


class OrderViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.DestroyModelMixin,
                   GenericViewSet):

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
