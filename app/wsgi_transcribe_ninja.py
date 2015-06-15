#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
WSGI config for prototype project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os
import newrelic.agent
newrelic.agent.initialize("app/conf/newrelic.ini")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings_transcribe_ninja")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
import newrelic.agent
newrelic.agent.initialize('/path/to/newrelic.ini')