#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import connection

from deployer.client import start

from deployer.node import Node

from app.deploy import hosts
from app.deploy.transcribe import TranscribeNinjaSystem

import app.settings_development as settings_development
import app.settings_production as settings_production


class RootNode(Node):

    """
    The root node of our configuration, containing two 'instances' of
    `WebSystem`,
    """
    # class DevelopmentSystem(TranscribeNinjaSystem):
    #     settings = settings_development

    #     class Hosts:
    #         web = {hosts.DevelopmentHost}
    #         database = {hosts.DatabaseHost}
            # engine = {hosts.DevelopmentHost}

    class ProductionSystem(TranscribeNinjaSystem):
        class Hosts:
            web = {hosts.WebHost}
            database = {hosts.DatabaseHost}
            engine = {hosts.EngineHost}


if __name__ == '__main__':
    start(RootNode)
