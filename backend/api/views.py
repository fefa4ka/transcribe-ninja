#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.contrib.auth import login, logout

from rest_framework import generics
from rest_framework import renderers
from rest_framework import viewsets
from rest_framework import mixins

from rest_framework.views import APIView

from rest_framework.decorators import api_view
from rest_framework.decorators import detail_route

from rest_framework.response import Response
from rest_framework.reverse import reverse

import backend.core.utils
from backend.core.models import *

from backend.api.serializers import *
from backend.api.permissions import *
from backend.api.authentication import *


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

    def create(self, request):
        serializer = RecordSerializer(data=request.data)

        if serializer.is_valid():
            obj = serializer.save(owner=request.user)
            backend.transcribe.utils.record_prepare.delay(obj)

            return Response(serializer.data)


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
            obj = serializer.save(owner=request.user)
            # backend.transcribe.utils.record_prepare.delay(obj)

            return Response(serializer.data)

    def get_queryset(self):
        return Order.objects.filter(owner=self.request.user)
