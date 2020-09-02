from lite_auth_http.app.models import UserInfo


def get_user_info_by_uid(uid):
    try:
        return UserInfo.objects.get(uid=uid)
    except:
        return None
