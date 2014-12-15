from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from django.contrib import admin
from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls import url, include

from backend.web import views

admin.autodiscover()

urlpatterns = patterns(
    '',
    (r'^admin/', include(admin.site.urls)),
    (r'^$', TemplateView.as_view(
        template_name="index.html")),
)

urlpatterns = format_suffix_patterns(urlpatterns)
