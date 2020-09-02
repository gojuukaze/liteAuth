#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    if 'gen_secret_key' in sys.argv:
        from django.core.management.utils import get_random_secret_key
        print("SECRET_KEY = '%s'" % get_random_secret_key())
        sys.exit()
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lite_auth_http.lite_auth_http.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
