import time
from datetime import timedelta

from django.conf import settings
from django.core.management import BaseCommand

from lite_auth_http.app.models import UserInfo
from lite_auth_http.notification.consts import NotificationType
from lite_auth_http.notification.manager import notify_user
from lite_auth_http.utils.log_writer import CmdLoggerWriter
from utils.datetime_helper import get_today_date


@CmdLoggerWriter('cron_logger')
class Command(BaseCommand):
    """
    python manage.py notify_password_expiration

    """

    def notify(self, user_info, days):
        print('notify', user_info.uid, days)
        user = user_info.user
        user._user_info = user_info
        notify_user(user, NotificationType.PasswordExpiration, days=days)

    def handle(self, *args, **options):
        days = settings.PASSWORD_EXPIRATION_NOTIFICATION.get('days', []) + [0]

        today = get_today_date()
        dates = [today - timedelta(days=(settings.MAX_PASSWORD_AGE - d)) for d in days]

        base_q = UserInfo.objects.filter(is_active=True, password_never_expire=False)

        for ui in base_q.filter(password_update_date__in=dates[:-1]):
            self.notify(ui, settings.MAX_PASSWORD_AGE - (today - ui.password_update_date).days)

        for ui in base_q.filter(password_update_date__lte=dates[-1]):
            self.notify(ui, 0)
