#!/usr/bin/python
# -*- coding: utf-8 -*-
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import DjangoFilterBackend

from django_filters import FilterSet, NumberFilter

from serializers import *

from api.permissions import *



# from core.models import *

# from api.serializers import *
# from api.authentication import *


class HistoryFilter(FilterSet):
    min_mistakes = NumberFilter(name="mistakes_length", lookup_type='gte')

    class Meta:
        model = Queue
        fields = [ 'id', 'min_mistakes' ]


class StandartResultSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class HistoryViewSet(ListAPIView):
    """
        Список кусков записи
    """
    model = Queue
    serializer_class = HistorySerializer
    permission_classes = (permissions.IsAuthenticated,
                          IsOwner,)
    pagination_class = StandartResultSetPagination
    filter_backends = (DjangoFilterBackend,)
    filter_class = HistoryFilter

    def get_queryset(self):
        user = self.request.user
        if 'checked' in self.request.QUERY_PARAMS:
            return user.account.queues(unchecked=False).filter(mistakes_length__gt=0).order_by('-checked')

        if 'unchecked' in self.request.QUERY_PARAMS:
            return user.account.queues(unchecked=True).order_by('-completed')

        return user.queue.filter(completed__isnull=False)
