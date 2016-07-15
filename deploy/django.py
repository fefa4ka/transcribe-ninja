#!/usr/bin/env python
# -*- coding: utf-8 -*-

# from app import settings

# from deployer.node import Node
from deployer.utils import esc1

import os.path

from aws import *


class DjangoDeployment(AWS):
    def update_hosts(self, hosts):
        self._put_template({
                "template": os.path.join(os.path.dirname(os.path.abspath(__file__)), 'conf/hosts.py.template'),
                "destination": "/home/%(EC2_SERVER_USERNAME)s/%(PROJECT_NAME)s/backend/app/hosts.py"
            }, hosts)

    def run_management_command(self, command):
        """ Run Django management command in virtualenv. """
        self._virtualenv('./manage.py %s' % esc1(command))

    def django_shell(self):
        """ Open interactive Django shell. """
        self.run_management_command('shell')

    def python_packages_install(self):
        """ Run Django management command in virtualenv. """
        # Activate the virtualenv.
        self._virtualenv('pip install --upgrade pip && pip install -r %(PROJECT_DIR)s/requirements/common.txt --upgrade' % settings.__dict__)
