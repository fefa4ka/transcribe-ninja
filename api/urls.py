#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf.urls import url, include
from django.conf import settings

from rest_framework.routers import DefaultRouter

from api import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
urlpatterns = ()

if settings.DOMAIN == "stenograph.us":
    router.register(r'records', views.RecordViewSet)
    router.register(r'orders', views.OrderViewSet)

    urlpatterns += (
        url(r'^api/records/(?P<record_id>.+)/pieces/$',
            views.PieceViewSet.as_view()),
    )

elif settings.DOMAIN == "transcribe.ninja":
    router.register(r'queue', views.QueueViewSet, "")
    router.register(r'transcriptions', views.TranscriptionViewSet)

    urlpatterns += (
        url(r'^api/statistics/$',
            views.StatisticsView.as_view()),
        url(r'^api/history/$',
            views.HistoryViewSet.as_view()),
    )




# The API URLs are now determined automatically by the router.
# Additionally, we include the login URLs for the browseable API.
urlpatterns += (
    url(r'api/', include(router.urls)),

    url(r'^api/auth/', include('djoser.urls')),
    url(r'^api/auth/basic',
        views.AuthView.as_view(),
        name='authenticate'),
    url(r'api/social/', include('social_auth.urls')),

    url(r'^api/account/',
        views.CurrentUserView.as_view()),

    # url(r'^api/queue/',
    #     views.QueueView.as_view()),

)
