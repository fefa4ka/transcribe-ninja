#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import settings

from deployer.node import Node
from deployer.utils import esc1

import boto

import os

class AWS(Node):

    def aws_connect(self):
        # Подключаемся к AWS
        return boto.ec2.connect_to_region(
            settings.EC2_REGION, aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

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

        name = security_group = "%s-%s" % (settings.PROJECT_NAME, name)

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


