from lite_auth_http.lite_auth_http.settings_common import *
from config import *

M_APPS = [
    'lite_auth_http.app',
    'lite_auth_http.app.apps.LiteAuthAdminConfig'

]
INSTALLED_APPS += M_APPS

AUTH_PASSWORD_VALIDATORS = []
for name, opt in PASSWORD_VALIDATORS.items():
    if name == 'CommonValidator':
        AUTH_PASSWORD_VALIDATORS.append({'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', })
    elif '.' in name:
        AUTH_PASSWORD_VALIDATORS.append({'NAME': name, 'OPTIONS': opt})
    else:
        AUTH_PASSWORD_VALIDATORS.append({'NAME': 'lite_auth_http.app.password_validation.' + name, 'OPTIONS': opt})

MIDDLEWARE += [
    'lite_auth_http.utils.middleware.password_age_middleware'
]

for k in list(NOTIFICATION_BACKEND.keys()):
    if '.' not in k:
        NOTIFICATION_BACKEND['lite_auth_http.notification.' + k] = NOTIFICATION_BACKEND.pop(k)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'verbose': {
            'format': '{asctime} {levelname} {module}.{funcName} Line:{lineno} {message}',
            'formatTime': '%Y-%m-%d %H:%M:%S',
            'style': '{',
        },
        'simple': {
            'format': '{asctime} {levelname} {message}',
            'formatTime': '%Y-%m-%d %H:%M:%S',
            'style': '{',

        },
        'simple2': {
            'format': '{asctime} {message}',
            'style': '{',
        },
        'only_message': {
            'format': '{message}',
            'style': '{',
        }
    },

    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },

        'default_err': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_PATH, 'error.log'),
            'formatter': 'verbose',
            'maxBytes': LOG_MAX_BYTES,
            'backupCount': LOG_BACKUP_COUNT,
        },
        'info': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_PATH, 'info.log'),
            'formatter': 'verbose',
            'maxBytes': LOG_MAX_BYTES,
            'backupCount': LOG_BACKUP_COUNT,
        },
        'cron': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_PATH, 'cron.log'),
            'formatter': 'only_message',
            'maxBytes': LOG_MAX_BYTES,
            'backupCount': LOG_BACKUP_COUNT,
        }
    },

    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': False,
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['default_err', 'console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'error_logger': {
            'handlers': ['default_err', 'console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'info_logger': {
            'handlers': ['info', 'console'] if DEBUG else ['info'],
            'level': 'INFO',
            'propagate': False,
        },
        'cron_logger': {
            'handlers': ['cron'],
            'level': 'INFO',
            'propagate': False,
        },

    }
}

CRONTAB_DJANGO_PROJECT_NAME = 'LiteAuth'
if 'crontab' in PASSWORD_EXPIRATION_NOTIFICATION:
    CRONJOBS = [
        (PASSWORD_EXPIRATION_NOTIFICATION['crontab'], 'django.core.management.call_command',
         ['notify_password_expiration']),
    ]
