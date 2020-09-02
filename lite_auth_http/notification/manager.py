import functools

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string
from django.core.checks import Error, register

from lite_auth_http.notification.consts import NotificationType
from lite_auth_http.utils.logger import error_logger


@register()
def notification_check(app_configs, **kwargs):
    try:
        get_notification_backends()
    except BaseException as e:

        return [Error(e, obj='Notification Backend')]
    return []


@functools.lru_cache(maxsize=None)
def get_notification_backends():
    backends = []
    for name, kwargs in settings.NOTIFICATION_BACKEND.items():
        try:
            klass = import_string(name)
        except ImportError:
            raise ImproperlyConfigured("找不到模块 %s ， 检查你的 NOTIFICATION_BACKEND 配置。" % name)
        backends.append(klass(**kwargs))
    return backends


def notify_user(user, type, **kwargs):
    try:
        for b in get_notification_backends():
            if type == NotificationType.PasswordExpired:
                b.send_password_expired_msg(user, **kwargs)
            elif type == NotificationType.LoginFailure:
                b.send_login_failure_msg(user, **kwargs)
            elif type == NotificationType.UserLocked:
                b.send_user_locked_msg(user, **kwargs)
    except BaseException as e:
        error_logger.error(e)


def notify_user2(user, title, msg):
    try:
        for b in get_notification_backends():
            b.send(user, title, msg)
    except BaseException as e:
        error_logger.error(e)
