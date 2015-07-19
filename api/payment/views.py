#!/usr/bin/python
# -*- coding: utf-8 -*-
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import DjangoFilterBackend
from rest_framework.status import HTTP_400_BAD_REQUEST

from django_filters import FilterSet, NumberFilter

from serializers import *

from api.permissions import *


from django.contrib.contenttypes.models import ContentType

from work.models import Account, Payment, Order, Queue, Price

from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

# from core.models import *

# from api.serializers import *
# from api.authentication import *


class PaymentFilter(FilterSet):
    object_type = NumberFilter(name="content_type", lookup_type='gte')

    class Meta:
        model = Payment
        fields = [ 'id', 'content_type' ]


class StandartResultSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class PaymentViewSet(mixins.ListModelMixin,
                   GenericViewSet):
    """
        Список кусков записи
    """
    model = Payment
    serializer_class = PaymentSerializer
    permission_classes = (permissions.IsAuthenticated,
                          IsOwner,)
    pagination_class = StandartResultSetPagination
    filter_backends = (DjangoFilterBackend,)
    filter_class = PaymentFilter

    def create(self, request):
        """
            Загрузка и создание записи
        """
        serializer = PaymentCreateSerializer(data=request.data)


        if serializer.is_valid():
            account_type_id = ContentType.objects.get_for_model(request.user.account).id
            price = Price.objects.filter(
                content_type_id=account_type_id,
                default=1
            )[0]

            # Считаем сколько на этот момент чувак может вывести бабла
            total = request.user.account.checked_balance * -1

            obj = serializer.save(owner=request.user, price=price, total=total, content_type_id=account_type_id, object_id=request.user.account.id)

            obj.save()

            return Response(serializer.data)
        else:
            errors = serializer.errors

        return Response(
            errors,
            status=HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        user = self.request.user
        account_object_id = ContentType.objects.get_for_model(Account).id

        return user.payments.filter(content_type_id=account_object_id).order_by('-created')
