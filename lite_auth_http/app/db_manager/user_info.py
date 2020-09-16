from lite_auth_http.app.models import UserInfo


def create_user_info(id, uid, name, **other_data):
    return UserInfo.objects.create(id=id, uid=uid, name=name,**other_data)


def get_user_info_by_uid(uid):
    try:
        return UserInfo.objects.get(uid=uid)
    except:
        return None
