#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Deploy
from deployer.host import SSHHost, LocalHost

from app import settings

import boto
import boto.ec2

class TranscribeNinjaHost(SSHHost):
    username = settings.EC2_SERVER_USERNAME
    key_filename = settings.EC2_KEY_PAIR

    @property
    def address(self):
        return self._aws_get_instance_address("%s-%s" % (settings.PROJECT_NAME, self.slug))


    def _aws_connect(self, service):
        # Подключаемся к AWS
        if service == "ec2":
            return boto.ec2.connect_to_region(
                settings.EC2_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        elif service == "rds":
            return boto.rds2.connect_to_region(
                settings.EC2_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

    def _aws_get_instance_address(self, name):
        # Сначала ищем среди EC2
        connection = self._aws_connect('ec2')

        reservations = connection.get_all_instances()

        for r in reservations:
            if r.instances[0].tags['Name'] == name:
                return r.instances[0].public_dns_name

        # Проверяем среди баз данных
        try:
            connection = self._aws_connect('rds')
            response = connection.describe_db_instances(name)
            print name
            return response['DescribeDBInstancesResponse']['DescribeDBInstancesResult']['DBInstances'][0]['Endpoint']['Address']
        except:
            pass

        return False



class DeployHost(TranscribeNinjaHost):
    slug = 'deploy'


class WebHost(TranscribeNinjaHost):
    slug = 'web'
    ports = [80, 22]


class DatabaseHost(TranscribeNinjaHost):
    slug = 'database'


class EngineHost(TranscribeNinjaHost):
    slug = 'engine'
    ports = [6379, 22]
