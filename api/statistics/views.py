#!/usr/bin/python
# -*- coding: utf-8 -*-
from rest_framework.views import APIView
from rest_framework.response import Response

from django.db.models import Sum
# from core.models import *

# from api.serializers import *
from api.permissions import *
# from api.authentication import *
from work.models import Queue, Payment

from django.contrib.contenttypes.models import ContentType


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
            "duration_check": 0,
            "total_price": 0
        }
        queues = None

        queue_object_id = ContentType.objects.get_for_model(Queue).id

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

                checked_queues_statistic = checked_queues.aggregate(work=Sum('work_length'), mistakes=Sum('mistakes_length'))

                statistics["checked_length"] = checked_queues_statistic['work'] - checked_queues_statistic['mistakes']

            queues_statistic = queues.aggregate(work=Sum('work_length'), mistakes=Sum('mistakes_length'))

            statistics["work_length"] = queues_statistic['work']
            statistics["mistakes_length"] = queues_statistic['mistakes']
            if 'checked' in self.request.QUERY_PARAMS:
                statistics["checked_length"] = queues_statistic['work'] - queues_statistic['mistakes']

            queues_ids = queues.values_list('id', flat=True).distinct()
            payments = Payment.objects.filter(content_type_id=queue_object_id, object_id__in=queues_ids).aggregate(total=Sum('total'))

            statistics['total_price'] = payments['total']
            return Response(statistics)
        except:
            return Response({"success": False})
