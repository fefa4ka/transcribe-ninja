#!/usr/bin/env python
# -*- coding: utf-8 -*-

from deployer.client import start

from deployer.node import Node

import hosts
from transcribe import TranscribeNinjaSystem

# import ..backend.app.settings.development as settings_development
# import backend.app.settings.production as settings_production


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
