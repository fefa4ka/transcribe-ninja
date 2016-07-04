#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include
from admin import admin_site
from django.http import HttpResponse


# print admin_site

# def my_view(request):
#     return HttpResponse("%s!" % request.__dict__)

#     context = dict(
#        # Include common variables for rendering the admin template.
#        self.admin_site.each_context(request),
#        # Anything else you want in the context...
#        key=value,
#     )
#     # return TemplateResponse(request, "sometemplate.html", context)


# def get_admin_urls(urls):
#     def get_urls():
#         my_urls = patterns('',
#             (r'^my_view/$', admin_site.admin_view(my_view))
#         )
#         return my_urls + urls
#     return get_urls

# admin_urls = get_admin_urls(admin_site.get_urls())
# admin_site.get_urls = admin_urls

urlpatterns = patterns(
    '',
    (r'^admin/', include(admin_site.urls)),
    (r'^admin/rq/', include('django_rq_dashboard.urls')),
    # (r'^admin_tools/', include('admin_tools.urls')),

)
