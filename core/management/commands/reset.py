#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection


class Command(BaseCommand):
    args = ''
    help = 'Drop and create database'

    def handle(self, *args, **options):
        dbinfo = settings.DATABASES['default']

        cursor = connection.cursor()
        cursor.execute("DROP DATABASE " + dbinfo["NAME"] + ";")
        cursor.execute("CREATE DATABASE " + dbinfo["NAME"] + " CHARACTER SET utf8 COLLATE utf8_general_ci;")
        cursor.execute("USE " + dbinfo["NAME"] + ";")
