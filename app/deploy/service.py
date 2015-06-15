#!/usr/bin/env python
# -*- coding: utf-8 -*-

from deployer.node import Node, required_property
from deployer.utils import esc1


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
