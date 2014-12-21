from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from django.contrib import admin
from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls import url, include
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns(
    '',
    (r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
	urlpatterns += patterns(
	    'django.contrib.staticfiles.views',
	    url(r'^(?:index.html)?$', 'serve', kwargs={'path': 'index.html'}),
	    url(r'^(?P<path>(?:js|css|img|data)/.*)$', 'serve'),
	)

urlpatterns = format_suffix_patterns(urlpatterns)
