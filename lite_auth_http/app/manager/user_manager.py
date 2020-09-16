from lite_auth_http.app import login_exceptions
from lite_auth_http.app.db_manager.password_history import create_password_history
from lite_auth_http.app.db_manager.user_info import create_user_info
from lite_auth_http.app.models import User
from lite_auth_http.notification.consts import NotificationType
from lite_auth_http.notification.manager import notify_user


def confirm_login_allowed(user, password, check_password_expired=True):
    user_info = user.user_info

    if not user_info.is_active:
        raise login_exceptions.Inactive()

    if user_info.is_lock():
        raise login_exceptions.TooManyLoginAttempts()

    if not user.check_password(password):
        user_info.add_try_count()
        if user_info.is_lock():
            notify_user(user, NotificationType.UserLocked)
        else:
            notify_user(user, NotificationType.LoginFailure, login_count=user_info.try_count)
        raise login_exceptions.Invalid(login_count=user_info.try_count)

    if check_password_expired and user_info.is_password_expired():
        notify_user(user, NotificationType.PasswordExpiration, days=0)
        raise login_exceptions.PasswordExpired()


def new_user(uid, name, password, groups=None, **user_info_attrs):
    u = User(username=uid, is_active=True)
    u.set_password(password)
    u.save()
    ui = create_user_info(u.id, uid, name, **user_info_attrs)
    create_password_history(uid, password=[u.password])
    if groups:
        ui.groups.set(groups)
