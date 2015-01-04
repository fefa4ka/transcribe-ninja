#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter

from api import views


# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'records', views.RecordViewSet)
router.register(r'orders', views.OrderViewSet)

router.register(r'transcriptions', views.TranscriptionViewSet)

# The API URLs are now determined automatically by the router.
# Additionally, we include the login URLs for the browseable API.
urlpatterns = (
    url(r'api/', include(router.urls)),

    url(r'^api/auth/',
        views.AuthView.as_view(),
        name='authenticate'),

    url(r'^api/account/',
        views.CurrentUserView.as_view()),

    url(r'^api/records/(?P<record_id>.+)/pieces/$',
        views.PieceViewSet.as_view()),

    url(r'^api/queue/',
        views.QueueView.as_view()),

)
