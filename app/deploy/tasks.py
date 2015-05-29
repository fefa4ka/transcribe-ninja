#!/usr/bin/env python
# -*- coding: utf-8 -*-

# from django.db import connection
from app import settings
from app.deploy.service import *
from app.deploy.django import *

import boto
import boto.ec2

import os.path

import time