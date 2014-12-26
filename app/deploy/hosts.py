# Deploy
from deployer.host import SSHHost, LocalHost

from app import settings 


class TranscribeNinjaHost(SSHHost):
    username = 'ubuntu'
    password = 'cntyjuhfa,kznm'
    key_filename = '/Users/fefa4ka/transcribe-eu.pem'


class DeployHost(TranscribeNinjaHost):
    slug = 'deploy'
    address = '54.93.50.120'


class WebHost(TranscribeNinjaHost):
    slug = 'web'
    address = settings.HOSTS['WEB']
    username = 'web'


class DatabaseHost(TranscribeNinjaHost):
    slug = 'database'
    address = settings.HOSTS['DB']


class EngineHost(TranscribeNinjaHost):
    slug = 'engine'
    address = settings.HOSTS['ENGINE']
    username = 'engine'
