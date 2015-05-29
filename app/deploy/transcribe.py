#!/usr/bin/env python
# -*- coding: utf-8 -*-

# from django.db import connection

from deployer.node import Node, map_roles
from deployer.utils import esc1

from app import settings
from app.deploy.service import *
from app.deploy.django import *
import app.deploy.tasks

import boto
import boto.ec2

import os.path

import time

class TranscribeNinjaSystem(DjangoDeployment):

    """
    The base definition of our web system.

    roles: web, engine, database
    """

    @map_roles(host='engine')
    class Supervisor(UpstartService):
        name = 'supervisor'
        config = '/etc/supervisor/conf.d/transcribe.conf'

    @map_roles(host='database')
    class Database(UpstartService):
        name = 'mysql'

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
        def clone(self):
            self.hosts.run("mkdir %s" % settings.PROJECT_DIR)

            with self.hosts.cd(settings.PROJECT_DIR, expand=True):
                self.hosts.run("git clone %s ." % settings.REPOSITORY)

        def checkout(self, commit):
            self.host.run("git checkout '%s'" % esc1(commit))

        def pull(self):
            with self.hosts.cd(settings.PROJECT_DIR, expand=True):
                self.hosts.run('git pull')

    @map_roles(host='web')
    class Frontend(DjangoDeployment):
        frontend_path = os.path.join(settings.PROJECT_DIR, 'frontend')

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

        def reset_db(self):
            self.run_management_command('reset')
            self.run_management_command('syncdb')

    @map_roles(host=('web', 'engine'))
    class EC2(AWS):
        def version(self):
            self.hosts.run('uname -a')

        def init(self):
            # start_time = time.time()
            print "Started..."

            # Генерим ключ
            self.aws_create_key()

            # Создаём машины
            for host in self.hosts.get_hosts():
                self.create_instance(host.slug, host.ports)

            print "Waiting 60 seconds for server to boot..."
            # time.sleep(60)

            # end_time = time.time()
            # print "Runtime: %f minutes" % ((end_time - start_time) / 60)

            # self.__create_database()
        def configure(self):
            # Настраиваем машины
            self.configure_instance('web', app.deploy.tasks.configure_instance)

    def deploy(self):
        self.Git.pull()

        self.Frontend.python_packages_install()
        self.Engine.python_packages_install()

        self.Uwsgi.restart()
        self.Nginx.restart()

        self.Supervisor.restart()

        self.Frontend.compile()


    # def configure_instance(self):
    #     # Настраиваем машины
    #     print app.deploy.tasks.configure_instance
    #     # self.configure_instance('web', app.deploy.tasks.configure_instance)


    # def __create_database(self):
    #     self.__create_postgresql()
    #     self.__create_redis()

