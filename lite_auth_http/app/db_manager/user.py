from django.contrib.auth import authenticate

from lite_auth_http.app.models import User


def create_user(uid, password, name) -> User:
    return User.objects.create_user(username=uid, password=password, is_staff=True, first_name=name, last_name=name)


def get_user_by_uid(uid) -> User:
    try:
        return User.objects.get(username=uid)
    except:
        return None


def authenticate_user(uid, password) -> User:
    return authenticate(username=uid, password=password)


def all_user():
    return User.objects.all()
