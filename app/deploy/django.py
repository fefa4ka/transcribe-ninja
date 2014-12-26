#!/usr/bin/env python
# -*- coding: utf-8 -*-

from deployer.node import Node
from deployer.utils import esc1

from app import settings


class DjangoDeployment(Node):
    activate_cmd = '. ~/bin/activate'

    def checkout_git(self, commit):
        self.host.run("git checkout '%s'" % esc1(commit))

    def git_pull(self):
        with self.hosts.cd(settings.PROJECT_DIRECTORY, expand=True):
            self.hosts.run('git pull')

    def run_management_command(self, command):
        """ Run Django management command in virtualenv. """
        # Activate the virtualenv.
        with self.hosts.prefix(self.activate_cmd):
            # Go to the directory where we have our 'manage.py' file.
            with self.hosts.cd('transcribe-ninja'):
                self.hosts.run('./manage.py %s' % esc1(command))

    def django_shell(self):
        """ Open interactive Django shell. """
        self.run_management_command('shell')
