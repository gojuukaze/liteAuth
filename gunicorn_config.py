"""
配置文件
运行：
gunicorn lite_auth_http.lite_auth_http.wsgi -c python:gunicorn_config
"""

import os

import config as lite_auth_config

bind = lite_auth_config.HTTP_LISTEN
proc_name = 'LiteAuthHttp'
pidfile = 'gunicorn.pid'

capture_output = True

workers = 3
worker_class = 'gevent'
# daemon = True

logconfig_dict = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(lite_auth_config.LOG_PATH, 'gunicorn.log'),
            'maxBytes': lite_auth_config.LOG_MAX_BYTES,
            'backupCount': lite_auth_config.LOG_BACKUP_COUNT,
        },
        'access': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(lite_auth_config.LOG_PATH, 'access.log'),
            'maxBytes': lite_auth_config.LOG_MAX_BYTES,
            'backupCount': lite_auth_config.LOG_BACKUP_COUNT,
        },
    },
    'loggers': {
        'gunicorn.error': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'gunicorn.access': {
            'handlers': ['access'],
            'level': 'INFO',
            'propagate': False,
        },

    },
}
