"""
docker用的config
"""

SECRET_KEY = '{{ secret_key }}'

_DOCKER_DATA_PATH = '/app/liteauth/docker_data/'

LOG_PATH = _DOCKER_DATA_PATH + 'log'
STATIC_ROOT = _DOCKER_DATA_PATH + 'static/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': _DOCKER_DATA_PATH + 'db.sqlite3',
    }
}

from docker_data.config import *
