#!/usr/bin/env python
# -*- coding: utf-8 -*-

from deployer.node import Node, required_property
from deployer.utils import esc1

from app import settings

import os


class UpstartService(Node):

    """
    Abstraction for any upstart service with start/stop/status methods.
    """
    name = required_property()

    def start(self):
        self.hosts.sudo('service %s start' % esc1(self.name))

    def stop(self):
        self.hosts.sudo('service %s stop' % esc1(self.name))

    def restart(self):
        self.stop()
        self.start()

    def status(self):
        self.hosts.sudo('service %s status' % esc1(self.name))

    def link_conf(self):
        with self.hosts.cd(settings.PROJECT_DIRECTORY, expand=True):
            project_directory = self.hosts.run('pwd')[0]
            print project_directory
            config_original = os.path.join(
                project_directory.rstrip(),
                "app/conf/%s.conf" % self.name)

            self.hosts.sudo("rm -rf %s" % esc1(self.config))
            self.hosts.sudo("ln -s %s %s" % (
                esc1(config_original),
                esc1(self.config))
            )
