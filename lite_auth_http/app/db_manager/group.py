from lite_auth_http.app.models import Group


def create_group(gid, desc=''):
    return Group.objects.create(gid=gid, desc=desc)
