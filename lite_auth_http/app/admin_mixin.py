import json

from django.conf import settings
from django.contrib.admin.options import IS_POPUP_VAR
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.db import transaction
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext as _, gettext_lazy

from lite_auth_http.app.forms import UserAddForm
from lite_auth_http.app.models import UserInfo, User, PasswordHistory
from django.contrib import admin, messages


class UserFormMixin:
    def get_fieldsets(self, request, obj=None):
        f = []
        if request.resolver_match.url_name == 'app_userinfo_add':
            f = [
                ('用户名', {'fields': ('uid',)}),
                ('密码', {'fields': (('password', 'reset_password',),)}),
                ('属性', {'fields': ('name', 'mail', 'mobile', 'ssh_key')}),
            ]
        elif request.resolver_match.url_name == 'app_userinfo_change':
            f = [
                ('用户名', {'fields': ('uid',)}),
                ('属性', {'fields': ('name', 'mail', 'mobile', 'ssh_key')}),
            ]
        if f and request.user.is_admin():
            f.append(('其他', {'fields': UserInfo.other_fields()[1:], 'classes': ('collapse',)}))
        return f or super().get_fieldsets(request, obj)

    def get_form(self, request, obj=None, change=False, **kwargs):
        # 不能用change判断，修改时get_form会调两次，第一次change为false
        if request.resolver_match.url_name == 'app_userinfo_add':
            kwargs['form'] = UserAddForm
        return super().get_form(request, obj, change, **kwargs)

    def get_readonly_fields(self, request, obj=None):

        if request.resolver_match.url_name == 'app_userinfo_change':
            if request.user.is_admin():
                return []
            return settings.READONLY_ATTRIBUTES + UserInfo.other_fields()
        return super().get_readonly_fields(request, obj)


class PermissionMixin:
    def has_module_permission(self, request):
        if request.user.is_anonymous:
            return False
        return request.user.is_admin()

    def has_view_permission(self, request, obj=None):
        return request.user.is_admin()

    def has_add_permission(self, request):
        return request.user.is_admin()

    def has_change_permission(self, request, obj=None):
        return request.user.is_admin()

    def has_delete_permission(self, request, obj=None):
        return request.user.is_admin()


class DeleteMixin:
    def response_delete(self, request, obj_display, obj_id):
        response = super().response_delete(request, obj_display, obj_id)
        if request._messages:
            other = []
            error = []
            for m in request._messages:
                if m.level == messages.ERROR:
                    error.append(m)
                else:
                    other.append(m)
            request._messages._queued_messages = error or other
        return response
