from django.conf import settings
from django.db import transaction

from lite_auth_http import consts
from lite_auth_http.app.db_manager.group import create_group
from lite_auth_http.app.manager.user_manager import new_user


def init2(data):
    from lite_auth_http.app.admin_forms import UserAddWithGroupsForm

    with transaction.atomic():
        # 1. 创建管理员组
        # group = create_group(consts.ADMIN_GROUP, '管理员组')
        admin_form = UserAddWithGroupsForm({'uid'})

        # 2. 创建管理员用户
        new_user(data['uid'], data['name'], data['password'], [group])
        # 3. 创建ldap用户
        new_user(data['ldap_uid'], data['ldap_uid'], data['ldap_password'])


def init(forms):
    with transaction.atomic():
        for f in forms:
            u = f.save()
            if u.uid == settings.LDAP_USER:
                u.password_never_expire = True
                u.save()
