#!/usr/bin/python
# -*- coding: utf-8 -*-
from rest_framework.views import APIView
from rest_framework.response import Response

from api.queue.views import *
from api.statistics.views import *
from api.history.views import *
from api.authentication import *


# from lazysignup.decorators import allow_lazy_user


class AuthView(APIView):

    """
        Класс аутентификации.
        post    - залогиниться
        delete  - разлогиниться
    """
    authentication_classes = (QuietBasicAuthentication,)

    def get(self, request):
        # Если не залогинен, то отдаё пустой ответ
        if not request.user.id:
            return Response({})

        serializer = UserSerializer(
            request.user,
            context={'request': request})
        return Response(serializer.data)

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
