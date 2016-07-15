#!/usr/bin/env python
# -*- coding: utf-8 -*-


from deployer.node import Node
from deployer.utils import esc1


import boto
import boto.rds2

import os
import time

import sys
sys.path.insert(0, '..')
from  backend.app.settings import production as settings


class AWS(Node):
    def get_address(self):
        hosts = [] 
        for host in self.hosts.get_hosts():
            host = host()
            hosts.append((host.slug, host.address))

        return hosts

    def _ec2_create(self, configs):
        start_time = time.time()
        print "Started..."

        connection = self._aws_connect('ec2')

        # Генерим ключ
        self._ec2_create_key()

        # Создаём машины
        for host in self.hosts.get_hosts():
            name = "%s-%s" % (settings.PROJECT_NAME, host.slug)
            print name
            # Проверяем, создана ли машина
            instance = self._ec2_get_instance(name)

            if not instance:
                # Получаем айпишник
                address = connection.allocate_address()

                instance = self._ec2_create_instance(host.slug, host.ports)

                # Прикрепляем айпишник
                connection.associate_address(
                    instance.id,
                    address.public_ip
                )

                print "Waiting 2 minutes for server to boot..."
                time.sleep(125)

                # Настраиваем
                for config in configs:
                    self._ec2_configure_instance(config)

        end_time = time.time()
        print "Runtime: %f minutes" % ((end_time - start_time) / 60)

        # self.__create_database()
    def _aws_connect(self, service):
        # Подключаемся к AWS
        if service == "ec2":
            return boto.ec2.connect_to_region(
                settings.EC2_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        elif service == "s3":
            return boto.s3.connection.S3Connection(
                settings.AWS_ACCESS_KEY_ID,
                settings.AWS_SECRET_ACCESS_KEY)
        elif service == "rds":
            return boto.rds2.connect_to_region(
                settings.EC2_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

    def _ec2_create_instance(self, name, tcp_ports):
        connection = self._aws_connect('ec2')

        name = security_group = "%s-%s" % (settings.PROJECT_NAME, name)

        # Проверяем, создана ли группа безопасности
        if not self._aws_get_security_group(security_group):
            # Создаём группу безопасности
            web = connection.create_security_group(security_group, '%s services' % name)
            for port in tcp_ports:
                web.authorize('tcp', int(port), int(port), '0.0.0.0/0')

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

        return instance

    def _ec2_configure_instance(self, tasks):
        # Configure the instance that was just created
        for item in tasks:
            try:
                print item['message']
            except KeyError:
                pass

            getattr(self, "_" + item['action'])(item['params'])

    def _ec2_get_project_instances(self):
        connection = self._aws_connect('ec2')

        reservations = connection.get_all_instances()
        instances = []

        for r in reservations:
            # Если в названии инстанта есть название проекта
            instance = r.instances[0]
            if settings.PROJECT_NAME in instance.tags['Name']:
                instances.append(instance)

        return instances

    def _ec2_get_instance(self, name):
        connection = self._aws_connect('ec2')

        reservations = connection.get_all_instances()

        for r in reservations:
            if r.instances[0].tags['Name'] == name:
                return r.instances[0]

        return False

    def _ec2_create_key(self):
        connection = self._aws_connect('ec2')

        # Проверяем наличие ключа на AWS
        if not connection.get_key_pair(settings.PROJECT_NAME):
            # Создаём, если нет
            key = connection.create_key_pair(settings.PROJECT_NAME)
            key.save(settings.EC2_KEY_PAIR_DIR)

        # Если не оказалось файла, создаём новый ключ
        if not os.path.isfile(settings.EC2_KEY_PAIR):
            self._ec2_delete_key()
            self._ec2_create_key()

    def _ec2_delete_key(self):
        connection = self._aws_connect('ec2')

        connection.delete_key_pair(settings.PROJECT_NAME)

        try:
            os.remove(settings.EC2_KEY_PAIR)
        except OSError:
            pass

    def _ec2_mysql_security_group(self):
        # Проверяем, создана ли группа безопасности
        # Доступ должны получить все машинки из группы проекта
        security_group_name = "%s-mysql" % settings.PROJECT_NAME
        security_group = self._aws_get_security_group(security_group_name)
        if not security_group:
            ec2_connection = self._aws_connect('ec2')
            # Создаём группу безопасности. разрешаем подключаться всем сервакам
            security_group = ec2_connection.create_security_group(security_group_name, '%s services' % security_group_name)
            for instance in self._ec2_get_project_instances():
                security_group.authorize('tcp', 3306, 3306, "%s/32" % instance.private_ip_address)

        return security_group

    # Проверяем есть ли нужная группа безопасности
    def _aws_get_security_group(self, name):
        connection = self._aws_connect('ec2')

        groups = connection.get_all_security_groups()

        for group in groups:
            if group.name == name:
                return group

        return None

    def _s3_create_bucket(self, bucket_name):
        from boto.s3.connection import Location
        connection = self._aws_connect('s3')
        return connection.create_bucket(bucket_name, location=Location.EU)

    # TODO: Создавать группу параметров с utf8
    def _rds_create_instance(self, db_instance_identifier, name, user, password):
        connection = self._aws_connect('rds')

        db_instance_identifier = "%s-%s" % (settings.PROJECT_NAME, db_instance_identifier)
        # Название таблицы только из букв состоит
        name = filter(str.isalpha, name)

        connection.create_db_instance(
            db_instance_identifier,
            settings.RDS_ALLOCATED_STORAGE,
            settings.RDS_INSTANCE_CLASS,
            settings.RDS_ENGINE,
            user,
            password,
            db_name=name,
            db_parameter_group_name='mysql-utf8',
            vpc_security_group_ids=[self._ec2_mysql_security_group().id],
            tags=[settings.PROJECT_NAME]
            )

    def _rds_get_instance(self, db_instance_identifier):
        connection = self._aws_connect('rds')

        db_instance_identifier = "%s-%s" % (settings.PROJECT_NAME, db_instance_identifier)

        try:
            response = connection.describe_db_instances(db_instance_identifier)

            return response['DescribeDBInstancesResponse']['DescribeDBInstancesResult']['DBInstances'][0].keys()

        except boto.rds2.exceptions.DBInstanceNotFound:
            return None



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
            self._sudo("apt-get install -y -qq %s" % pkg)

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

    def _put_template(self, params, context=settings.__dict__):
        """
        Same as _put() but it loads a file and does variable replacement
        """
        f = open(self._render(params['template']), 'r')
        template = f.read()

        self.hosts.run(
            self._write_to(
                self._render(template, context),
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
            with self.hosts.cd(os.path.join(settings.PROJECT_DIR, 'backend'), expand=True):
                self.hosts.run(self._render(command))
