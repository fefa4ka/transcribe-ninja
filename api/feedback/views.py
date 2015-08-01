#!/usr/bin/python
# -*- coding: utf-8 -*-
from rest_framework.response import Response
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.status import HTTP_400_BAD_REQUEST

import core.async_jobs

from serializers import *

from api.permissions import *


class FeedbackViewSet(mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet):

    """
        Заказ на транскрибцию
    """
    model = Feedback
    serializer_class = FeedbackSerializer


    def create(self, request):
        """
            Создание заказа
        """
        serializer = FeedbackSerializer(data=request.data)

        if serializer.is_valid():
            if request.user.is_anonymous():
                serializer.save()
            else:
                serializer.save(owner=request.user)

            return Response(serializer.data)
        else:
            errors = serializer.errors

        return Response(
            errors,
            status=HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        """
            Список заказов для текущего пользователя
        """
        if not self.request.user.is_anonymous():
            return Feedback.objects.filter(owner=self.request.user)
        else:
            return
