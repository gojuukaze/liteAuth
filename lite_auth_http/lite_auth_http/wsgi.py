"""
WSGI config for lite_auth_http project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os

from django.core.exceptions import ImproperlyConfigured
from django.core.wsgi import get_wsgi_application

from lite_auth_http.notification.manager import notification_check

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lite_auth_http.lite_auth_http.settings')

err = notification_check(None)
if err:
    raise ImproperlyConfigured(err[0].msg)

application = get_wsgi_application()


