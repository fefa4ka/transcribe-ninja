#!/usr/bin/env python
# -*- coding: utf-8 -*-

from deployer.node import Node, map_roles
from deployer.utils import esc1

from app import settings
from app.deploy.service import *
from app.deploy.django import *

import os.path


class TranscribeNinjaSystem(Node):

    """
    The base definition of our web system.

    roles: cache, queue, master_db, slave_db, web.
    """

    @map_roles(host='engine')
    class Supervisor(UpstartService):
        name = 'supervisor'
        config = '/etc/supervisor/conf.d/transcribe.confё'

    @map_roles(host='database')
    class Database(UpstartService):
        name = 'mysql'

        def reset(self):
            pass

    @map_roles(host='database')
    class Queue(UpstartService):
        name = 'redis-server'

    @map_roles(host='web')
    class Nginx(UpstartService):
        name = 'nginx'
        config = '/etc/nginx/sites-enabled/transcribe-ninja.conf'

    @map_roles(host='web')
    class Uwsgi(UpstartService):
        name = 'uwsgi'
        config = '/etc/uwsgi/apps-enabled/transcribe-ninja.ini'

    @map_roles(host=('web', 'engine'))
    class Git(Node):
        def checkout(self, commit):
            self.host.run("git checkout '%s'" % esc1(commit))

        def pull(self):
            with self.hosts.cd(settings.PROJECT_DIRECTORY, expand=True):
                self.hosts.run('git pull')

    @map_roles(host='web')
    class Frontend(DjangoDeployment):
        frontend_path = os.path.join(settings.PROJECT_DIRECTORY, 'frontend')

        def compile(self):
            with self.hosts.cd(self.frontend_path, expand=True):
                self.hosts.run('bower install')
                self.hosts.run('grunt clean')
                self.hosts.run('grunt --force')

            self.run_management_command('collectstatic --noinput')

    @map_roles(host='engine')
    class Engine(DjangoDeployment):

        def update(self):
            self.git_pull()

    def deploy(self):
        self.Git.pull()

        self.Uwsgi.restart()
        self.Nginx.restart()

        self.Supervisor.restart()

        self.Frontend.compile()
