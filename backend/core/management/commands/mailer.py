#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection


class Command(BaseCommand):
    args = ''
    help = ''

    def handle(self, *args, **options):
        pass
