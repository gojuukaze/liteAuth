import time

from django.conf import settings
from django.core.management import BaseCommand
import sys

from lite_auth_http.app.models import User, UserInfo, Group, PasswordHistory


class Command(BaseCommand):
    """
    python manage.py mock

    """

    def create_group(self, gid):
        return Group.objects.create(gid='admin')

    def create_user(self, uid, group, password):
        u = User(username=uid, is_active=True)
        u.set_password(password)
        u.save()
        ui = UserInfo.objects.create(id=u.id, uid=uid, name=uid)
        PasswordHistory.objects.create(uid=uid, password=[u.password])
        if group:
            ui.groups.add(group)

        return u, ui

    def handle(self, *args, **options):
        g = self.create_group('admin')

        self.create_user('admin', g, '1')

        _, ui = self.create_user(settings.LDAP_USER, None, '1')
        ui.password_never_expire = True
        ui.save()
