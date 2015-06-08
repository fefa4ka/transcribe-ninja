#!/usr/bin/env python
# -*- coding: utf-8 -*-

# from app import settings

# from deployer.node import Node
from deployer.utils import esc1

from app.deploy.aws import *


class DjangoDeployment(AWS):
    def update_hosts(self, hosts):
        self._put_template({
                "template": "%(BASE_DIR)s/app/conf/hosts.py.template",
                "destination": "/home/%(EC2_SERVER_USERNAME)s/%(PROJECT_NAME)s/app/hosts.py"
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
        self._virtualenv('pip install -r %(PROJECT_DIR)s/requirements/common.txt --upgrade' % settings.__dict__)
