#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Deploy
from deployer.host import SSHHost, LocalHost

from app import settings

import boto
import boto.ec2

class TranscribeNinjaHost(SSHHost):
    username = 'ubuntu'
    password = 'cntyjuhfa,kznm'
    key_filename = settings.EC2_KEY_PAIR

    @property
    def address(self):
        instance = self.aws_get_instance("%s-%s" % (settings.PROJECT_NAME, self.slug))

        if instance:
            return instance.public_dns_name

        return False

    def aws_connect(self):
        # Подключаемся к AWS
        return boto.ec2.connect_to_region(
            settings.EC2_REGION, aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

    def aws_get_instance(self, name):
        connection = self.aws_connect()

        reservations = connection.get_all_instances()

        for r in reservations:
            if r.instances[0].tags['Name'] == name:
                return r.instances[0]

        return False



class DeployHost(TranscribeNinjaHost):
    slug = 'deploy'
    address = '54.93.50.120'


class WebHost(TranscribeNinjaHost):
    slug = 'web'
    # address = settings.HOSTS['WEB']
    # username = 'web'


class DatabaseHost(TranscribeNinjaHost):
    slug = 'database'
    # address = settings.HOSTS['DB']


class EngineHost(TranscribeNinjaHost):
    slug = 'engine'
    # address = settings.HOSTS['ENGINE']
    # username = 'engine'
