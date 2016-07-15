#!/usr/bin/env python
# -*- coding: utf-8 -*-

# from django.db import connection

from deployer.node import Node, map_roles
from deployer.utils import esc1

from service import *
from django import *
import tasks as tasks

import os.path

import sys
sys.path.insert(0, '..')
import backend.app.settings.production as settings


class TranscribeNinjaSystem(Node):

    """
    The base definition of our web system.

    roles: web, engine, database
    """

    @map_roles(host='database')
    class Database(AWS):
        def create(self):
            host = settings.DATABASES['default']

            # Создаём группу безопасности
            security_group = self._ec2_mysql_security_group()
            # Создаём группу параметров

            # Запускаем инстанс
            self._rds_create_instance(
                'database',
                host['NAME'],
                host['USER'],
                host['PASSWORD'])

    @map_roles(host='database')
    class Queue(UpstartService):
        name = 'redis-server'

    @map_roles(host=('web', 'engine'))
    class Application(DjangoDeployment):
        def create_storage(self):
            # Создаём бакет для файлов
            bucket = self._s3_create_bucket(settings.AWS_STORAGE_BUCKET_NAME)

            self.config_bucket()

        def clang(self):
            self.hosts.run('export C_INCLUDE_PATH=/usr/local/Cellar/libxml2/2.9.2/include/libxml2:$C_INCLUDE_PATH')

        def config_bucket(self):
            from boto.s3.cors import CORSConfiguration
            connection = self._aws_connect('s3')

            bucket = connection.lookup(settings.AWS_STORAGE_BUCKET_NAME)

            # Чтобы могли загружать файл с других сайтов
            cors_cfg = CORSConfiguration()
            cors_cfg.add_rule('GET', '*')
            bucket.set_cors(cors_cfg)

        def update(self):
            self.checkout()
            self.pull()

        def checkout(self, commit="."):
            with self.hosts.cd(settings.PROJECT_DIR, expand=True):
                self.hosts.run("git checkout '%s'" % esc1(commit))

        def pull(self):
            with self.hosts.cd(settings.PROJECT_DIR, expand=True):
                self.hosts.run('git pull')

    @map_roles(host='web')
    class Frontend(DjangoDeployment):
        frontend_path = os.path.join(settings.PROJECT_DIR, 'frontend')

        def create(self):
            self._ec2_create([
                tasks.common_configure,
                tasks.web_configure
            ])

        def restart(self):
            self._ec2_configure_instance(tasks.reload_nginx + tasks.reload_uwsgi)
            self.compile()

        def compile(self):
            with self.hosts.prefix(settings.ACTIVATE):
                with self.hosts.cd(self.frontend_path, expand=True):
                    self.hosts.run('bash build.sh')

            self.run_management_command('collectstatic --noinput --settings=app.settings.transcribe_ninja')
            self.run_management_command('collectstatic --noinput --settings=app.settings.stenograph_us')

    @map_roles(host='engine')
    class Engine(DjangoDeployment):
        def create(self):
            self._ec2_create([
                tasks.common_configure,
                tasks.engine_configure
            ])

        def restart(self):
            self._ec2_configure_instance(tasks.reload_supervisor)

        def migrate(self):
            self.run_management_command('migrate --settings=app.settings.stenograph_us')

        def reset_db(self):
            self.run_management_command('reset')
            self.run_management_command('syncdb --settings=app.settings.stenograph_us')

    def create(self):
        # Если созданы — удалить
        # Предварительно спросить
        self.Frontend.create()

        self.Engine.create()

        # S3 Bucket
        self.Application.create_storage()

        # Создаём базы
        self.Database.create()

        # Меняем хосты в конфиге
        self.update_hosts()

        self.Engine.reset_db()

        self.deploy()

    def update_hosts(self):
        self.Application.update_hosts({
            "ENGINE": self.Engine.get_address()[0][1],
            "WEB": self.Frontend.get_address()[0][1],
            "DATABASE": self.Database.get_address()[0][1]
        })

    def print_hosts(self):
        hosts = []
        hosts += self.Application.get_address()
        hosts += self.Database.get_address()

        for host in hosts:
            print "%s:\t%s" % (host[0], host[1])


    def deploy(self):
        self.Application.update()

        self.Application.python_packages_install()

        self.update_hosts()

        self.Engine.migrate()

        self.Frontend.restart()

        self.Engine.restart()


    def frontend_deploy(self):
        self.Application.update()
        self.update_hosts()
        self.Frontend.restart()

    def backend_deploy(self):
        self.Application.update()
        self.update_hosts()
        self.Engine.restart()

