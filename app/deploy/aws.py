#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import settings

from deployer.node import Node
from deployer.utils import esc1

import boto

import os
import time

class AWS(Node):

    def aws_connect(self):
        # Подключаемся к AWS
        return boto.ec2.connect_to_region(
            settings.EC2_REGION, aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

    def create(self, configs):
        # start_time = time.time()
        print "Started..."

        # Генерим ключ
        self.aws_create_key()

        # Создаём машины
        for host in self.hosts.get_hosts():
            self.create_instance(host.slug, host.ports)

        print "Waiting 2 minutes for server to boot..."
        time.sleep(125)

        for config in configs:
            self.configure_instance(config)

        end_time = time.time()
        print "Runtime: %f minutes" % ((end_time - start_time) / 60)

        # self.__create_database()

    # Проверяем есть ли нужная группа безопасности
    def aws_check_security_group_exist(self, name):
        connection = self.aws_connect()

        groups = connection.get_all_security_groups()

        for group in groups:
            if group.name == name:
                return True

        return False

    def create_instance(self, name, tcp_ports):
        connection = self.aws_connect()

        name = security_group = "%s-%s-test" % (settings.PROJECT_NAME, name)

        # Проверяем, создана ли группа безопасности
        if not self.aws_check_security_group_exist(security_group):
            # Создаём группу безопасности
            web = connection.create_security_group(security_group, '%s services' % name)
            for port in tcp_ports:
                web.authorize('tcp', int(port), int(port), '0.0.0.0/0')

        # Проверяем, создана ли машина
        instance = self.aws_get_instance(name)

        if not instance:
            # Создаём машину
            print "Creating instance %s" % name
            reservation = connection.run_instances(
                settings.EC2_AMI,
                key_name=settings.PROJECT_NAME,
                instance_type=settings.EC2_INSTANCE_TYPE,
                security_groups=[security_group])


            # Ждём пока запустится
            instance = reservation.instances[0]
            connection.create_tags([instance.id], { "Name": name })

            while instance.state == u'pending':
                print "Instant state: %s" % instance.state
                time.sleep(10)
                instance.update()

            print "Public DNS name of %s: %s" % (name, instance.public_dns_name)

        return instance.public_dns_name

    def configure_instance(self, tasks):
        # Configure the instance that was just created
        for item in tasks:
            try:
                print item['message']
            except KeyError:
                pass

            getattr(self, "_" + item['action'])(item['params'])

    def aws_get_instance(self, name):
        connection = self.aws_connect()

        reservations = connection.get_all_instances()

        for r in reservations:
            if r.instances[0].tags['Name'] == name:
                return r.instances[0]

        return False

    def aws_create_key(self):
        connection = self.aws_connect()

        # Проверяем наличие ключа на AWS
        if not connection.get_key_pair(settings.PROJECT_NAME):
            # Создаём, если нет
            key = connection.create_key_pair(settings.PROJECT_NAME)
            key.save(settings.EC2_KEY_PAIR_DIR)

        # Если не оказалось файла, создаём новый ключ
        if not os.path.isfile(settings.EC2_KEY_PAIR):
            self.aws_delete_key()
            self.aws_create_key()

    def aws_delete_key(self):
        connection = self.aws_connect()

        connection.delete_key_pair(settings.PROJECT_NAME)

        try:
            os.remove(settings.EC2_KEY_PAIR)
        except OSError:
            pass


    # Actions
    # def _virtualenv(params):
    #     """
    #     Allows running commands on the server
    #     with an active virtualenv
    #     """
    #     with cd(fabconf['APPS_DIR']):
    #         _virtualenv_command(_render(params))
    def _apt(self, params):
        """
        Runs apt-get install commands
        """
        for pkg in params:
            self._sudo("apt-get install -qq %s" % pkg)

    def _pip(self, params):
        """
        Runs pip install commands
        """
        for pkg in params:
            self._sudo("pip install %s" % pkg)

    def _run(self, params):
        """
        Runs command with active user
        """
        command = self._render(params)
        self.hosts.run(command)

    def _sudo(self, params):
        """
        Run command as root
        """
        command = self._render(params)
        self.hosts.sudo(command)

    def _put(self, params):
        """
        Moves a file from local computer to server
        """
        for host in self.hosts.get_hosts():
            host = host()
            host.put_file(
                self._render(params['file']),
                self._render(params['destination'])
            )

    def _put_template(self, params):
        """
        Same as _put() but it loads a file and does variable replacement
        """
        f = open(self._render(params['template']), 'r')
        template = f.read()

        self.hosts.run(
            self._write_to(
                self._render(template),
                self._render(params['destination'])
            )
        )

    def _render(self, template, context=settings.__dict__):
        """
        Does variable replacement
        """
        return template % context

    def _write_to(self, string, path):
        """
        Writes a string to a file on the server
        """
        return "echo '" + string + "' > " + path

    def _append_to(self, string, path):
        """
        Appends to a file on the server
        """
        return "echo '" + string + "' >> " + path

    def _virtualenv(self, command):
        """
        Activates virtualenv and runs command
        """
        with self.hosts.prefix(settings.ACTIVATE):
            with self.hosts.cd(settings.PROJECT_DIR, expand=True):
                self.hosts.run(self._render(command))
