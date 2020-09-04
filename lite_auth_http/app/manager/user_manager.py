from lite_auth_http.app import login_exceptions
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
