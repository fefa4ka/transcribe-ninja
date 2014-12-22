#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.contrib.auth import login, logout

from rest_framework import generics
from rest_framework import renderers
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import status

from rest_framework.views import APIView

from rest_framework.decorators import api_view
from rest_framework.decorators import detail_route

from rest_framework.response import Response
from rest_framework.reverse import reverse

import transcribe.utils
import core.async_jobs

from core.models import *

from api.serializers import *
from api.permissions import *
from api.authentication import *

import django_rq


class AuthView(APIView):
    authentication_classes = (QuietBasicAuthentication,)

    def post(self, request, *args, **kwargs):
        print request.user.email
        login(request, request.user)

        return Response(UserSerializer(request.user, context={'request': request}).data)

    def delete(self, request, *args, **kwargs):
        logout(request)

        return Response({})


class UserViewSet(viewsets.ReadOnlyModelViewSet):

    """
    This viewset automatically provides `list` and `detail` actions.
    """
    model = User
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,
                          IsOwner,)

    def dispatch(self, request, *args, **kwargs):
        if kwargs.get('pk') == 'current' and request.user:
            kwargs['pk'] = request.user.pk

        return super(UserViewSet, self).dispatch(request, *args, **kwargs)


class CurrentUserView(APIView):
    queryset = User

    def get(self, request):
        if not request.user.id:
            return Response({})

        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)


class RecordViewSet(mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):

    """
    Record

    """
    queryset = Record.objects.all()
    serializer_class = RecordSerializer
    permission_classes = (permissions.IsAuthenticated,
                          IsOwner,)

    # @detail_route(renderer_classes=[renderers.StaticHTMLRenderer])
    # def transcription(self, request, *args, **kwargs):
    #     record = self.get_object()
    #     return Response(record.title)
    def get_queryset(self):
        """
        This view should return a list of all the purchases for
        the user as determined by the username portion of the URL.
        """
        return Record.objects.filter(owner=self.request.user)

    def create(self, request):
        serializer = RecordSerializer(data=request.data)

        if serializer.is_valid():
            # queue = django_rq.get_queue('web')
            # queue.enqueue(serializer.save, owner=request.user)
            # transcribe.utils.record_save.delay(serializer)
            obj = serializer.save(owner=request.user)
            core.async_jobs.record_prepare.delay(obj)

            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PieceViewSet(generics.ListAPIView):

    """
    This viewset automatically provides `list` and `detail` actions.
    """
    model = Piece
    serializer_class = PieceSerializer
    permission_classes = (permissions.IsAuthenticated,
                          IsOwner,)

    def get_queryset(self):
        """
        This view should return a list of all the purchases for
        the user as determined by the username portion of the URL.
        """
        record_id = self.kwargs['record_id']
        return Piece.objects.filter(record_id=record_id)


class RecordTranscription(generics.GenericAPIView):
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
    This viewset automatically provides `list` and `detail` actions.
    """
    model = Order
    serializer_class = OrderSerializer
    permission_classes = (permissions.IsAuthenticated,
                          IsOwner,)

    def create(self, request):
        serializer = OrderSerializer(data=request.data)

        if serializer.is_valid():
            duration = float(request.data['end_at']) - float(request.data['start_at'])

            if duration > 0:
                object_id = ContentType.objects.get_for_model(Order).id
                price = Price.objects.filter(
                    content_type_id=object_id,
                    default=1
                )[0]

                total = price.price * duration / 60

                if request.user.account.balance >= total:
                    obj = serializer.save(owner=request.user, price=price)
                    core.async_jobs.make_queue.delay(obj)
                    return Response(serializer.data)
                else:
                    errors = [{'balance': 'Not enought money.'}]
            else:
                errors = [{'end_at': 'End_at should be greater that start_at'}]
                pass
        else:
            errors = serializer.errors
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        return Order.objects.filter(owner=self.request.user)
