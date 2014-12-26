#!/usr/bin/env python
# -*- coding: utf-8 -*-

from deployer.client import start

from deployer.node import Node

from app.deploy import hosts
from app.deploy.transcribe import TranscribeNinjaSystem


class RootNode(Node):

    """
    The root node of our configuration, containing two 'instances' of
    `WebSystem`,
    """
    class LocalSystem(TranscribeNinjaSystem):

        class Hosts:
            web = {hosts.LocalHost}
            database = {hosts.LocalHost}
            engine = {hosts.LocalHost}
            deploy = {hosts.DeployHost}

    class ProductionSystem(TranscribeNinjaSystem):

        class Hosts:
            web = {hosts.WebHost}
            database = {hosts.DatabaseHost}
            engine = {hosts.EngineHost}


if __name__ == '__main__':
    start(RootNode)
