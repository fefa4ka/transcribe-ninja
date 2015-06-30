#!/usr/bin/python
# -*- coding: utf-8 -*-
from rest_framework.views import APIView
from rest_framework.response import Response

from core.models import *

from api.serializers import *
from api.permissions import *
from api.authentication import *


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

        try:

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

                if 'checked' in self.request.QUERY_PARAMS:
                    statistics["checked_length"] += queue.work_length - queue.mistakes_length

                if queue.work_type == Queue.TRANSCRIBE:
                    statistics["duration_transcribe"] += queue.duration
                elif queue.work_type == Queue.EDIT:
                    statistics["duration_check"] += queue.duration

            return Response(statistics)
        except:
            return Response({"success": False})
