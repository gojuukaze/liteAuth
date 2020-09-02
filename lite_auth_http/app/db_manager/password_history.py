from lite_auth_http.app.models import PasswordHistory


def create_password_history(uid, password=None):
    if password is None:
        password = []
    return PasswordHistory.objects.create(uid=uid, password=password)


def get_password_history_by_uid(uid):
    try:
        return PasswordHistory.objects.get(uid=uid)
    except:
        return None
