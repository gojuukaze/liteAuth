from django.conf import settings
from django.core.management import BaseCommand


class Command(BaseCommand):
    """
    python manage.py show_secret_key

    """

    def handle(self, *args, **options):
        print("SECRET_KEY='%s'"%settings.SECRET_KEY)
