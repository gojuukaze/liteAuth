import re

from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin.options import IS_POPUP_VAR
from django.contrib.admin.utils import unquote
from django.utils.html import escape
from django.utils.translation import gettext as _, gettext_lazy

# Register your models here.
from django.contrib.auth.models import Group as AuthGroup
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin, sensitive_post_parameters_m
from django.core.exceptions import PermissionDenied

from django.db import transaction
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.utils.safestring import mark_safe

from lite_auth_http import consts
from lite_auth_http.app.admin_actions import delete_selected
from lite_auth_http.app.admin_mixin import UserFormMixin, PermissionMixin, DeleteMixin
from lite_auth_http.app.admin_forms import ChangeUserPasswordForm
from lite_auth_http.app.models import UserInfo, Group, User, PasswordHistory
from utils.datetime_helper import get_today_date

admin.site.disable_action('delete_selected')
admin.site.add_action(delete_selected)


class UserGroupInline(PermissionMixin, admin.StackedInline):
    model = Group.users.through
    extra = 1
    verbose_name = '用户所属组'
    verbose_name_plural = '组/groups'

    def has_view_permission(self, request, obj=None):

        if request.user.is_admin():
            return True
        if request.resolver_match.url_name == 'app_userinfo_change':
            id = re.findall(r'/app/userinfo/(\d+)/change/', request.get_full_path())[0]
            return int(id) == request.user.id
        return False

    def has_add_permission(self, request, obj):
        return request.user.is_admin()


@admin.register(UserInfo)
class UserAdmin(UserFormMixin, PermissionMixin, DeleteMixin, admin.ModelAdmin):
    list_display = ['uid', 'name', 'is_active', ]
    list_editable = ['is_active']
    list_filter = (
        ('is_active', admin.BooleanFieldListFilter),
        ('groups', admin.RelatedOnlyFieldListFilter),
    )
    save_as_continue = True
    inlines = [UserGroupInline]
    change_list_template = 'admin_ex/user_list.html'

    def change_password(self, obj):
        return mark_safe('<a href="%s">修改密码</a>' % reverse('admin:password_change'))

    change_password.short_description = '修改密码'

    def change_everyone_password(self, obj):
        return mark_safe('<a href="%s">修改密码</a>' % reverse('admin:auth_user_password_change', args=[obj.id]))

    change_everyone_password.short_description = '修改密码'

    def get_list_display(self, request):
        if request.user.is_admin():
            return self.list_display + ['change_everyone_password']
        return self.list_display + ['change_password']

    def get_queryset(self, request):
        qs = super(UserAdmin, self).get_queryset(request)
        if not request.user.is_admin():
            qs = qs.filter(uid=request.user.username)
        return qs

    def save_model(self, request, obj, form, change):
        if not change:
            with transaction.atomic():
                user = form.user
                user.save()
                obj.id = user.id
                obj.save()
                from lite_auth_http.app.db_manager.password_history import create_password_history
                create_password_history(obj.uid, password=[user.password])
        else:
            return obj.save()

    def delete_queryset(self, request, queryset):

        uids = list(queryset.values_list('uid', flat=True))
        if settings.LDAP_USER in uids:
            return '包含了不能删除的用户（%s）' % settings.LDAP_USER
        if request.user.username in uids:
            return '不能删除自己'
        with transaction.atomic():
            queryset.delete()
            User.objects.filter(username__in=uids).delete()
            PasswordHistory.objects.filter(uid__in=uids).delete()

    def delete_model(self, request, obj):
        if settings.LDAP_USER == obj.uid:
            self.message_user(request, '不能删除ldap用户（%s）' % settings.LDAP_USER, messages.ERROR)
            return
        if request.user.username == obj.uid:
            self.message_user(request, '不能删除自己')
            return
        with transaction.atomic():
            obj.user.delete()
            obj.password_history.delete()
            obj.delete()

    # todo 从admin组移除用户校验
    # def save_related(self, request, form, formsets, change):
    #     # 如果增加了其他inlines，这里需要重写
    #     if formsets:
    #         gu_formsets=formsets[0]
    #         for f in gu_formsets:
    #             if f.cleaned_data['DELETE']==True and f.cleaned_data['group'].gid==consts.ADMIN_GROUP:
    #             if isinstance(f, forms.BaseFormSet):
    #                 for f2 in f:
    #                     
    #                     print(type(f2))
    #             # print(f.cleaned_data)
    # 
    #     return super(UserAdmin, self).save_related(request, form, formsets, change)

    def has_view_permission(self, request, obj=None):
        if request.user.is_admin():
            return True
        if request.resolver_match.url_name == 'app_userinfo_change':
            id = re.findall(r'/app/userinfo/(\d+)/change/', request.get_full_path())[0]
            return int(id) == request.user.id
        # 注意这里是返回true，默认有浏览权限，否则首页不会显示model
        return True

    def has_change_permission(self, request, obj=None):
        if request.user.is_admin():
            return True
        if request.resolver_match.url_name == 'app_userinfo_change':
            id = re.findall(r'/app/userinfo/(\d+)/change/', request.get_full_path())[0]
            return int(id) == request.user.id
        return False

    def has_module_permission(self, request):
        if request.user.is_anonymous:
            return False
        return True


@admin.register(Group)
class GroupAdmin(PermissionMixin, DeleteMixin, admin.ModelAdmin):
    filter_horizontal = ('users',)

    def delete_queryset(self, request, queryset):

        if queryset.filter(gid=consts.ADMIN_GROUP).count() > 0:
            return '包含了不能删除的组（%s）' % consts.ADMIN_GROUP

        return super(GroupAdmin, self).delete_queryset(request, queryset)

    def delete_model(self, request, obj):
        if consts.ADMIN_GROUP == obj.gid:
            self.message_user(request, '不能删除组 %s' % consts.ADMIN_GROUP, messages.ERROR)
            return
        return super(GroupAdmin, self).delete_model(request, obj)

    # todo 从admin组移除用户校验
    # def save_form(self, request, form, change):
    #     print(form.cleaned_data)
    #     # form.add_error('users', forms.ValidationError('hhh'))
    #     # raise forms.ValidationError('hhh')
    #     return None
    #     return super(GroupAdmin, self).save_form(request, form, change)
    # 
    # def save_related(self, request, form, formsets, change):
    #     print(form.cleaned_data)
    #     # 如果增加了其他关系，这里需要重写
    #     for f in formsets:
    #         print(f.cleaned_data)
    # 
    #     return super(GroupAdmin, self).save_related(request, form, formsets, change)


@admin.register(User)
class LiteAuthUserAdmin(PermissionMixin, AuthUserAdmin):
    change_password_form = ChangeUserPasswordForm

    def has_module_permission(self, request):
        return False

    @sensitive_post_parameters_m
    def user_change_password(self, request, id, form_url=''):
        user = self.get_object(request, unquote(id))
        if not self.has_change_permission(request, user):
            raise PermissionDenied
        if user is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {
                'name': self.model._meta.verbose_name,
                'key': escape(id),
            })
        if request.method == 'POST':
            form = self.change_password_form(user, request.POST)
            if form.is_valid():
                with transaction.atomic():
                    form.save()
                change_message = self.construct_change_message(request, form, None)
                self.log_change(request, user, change_message)
                msg = _('Password changed successfully.')
                messages.success(request, msg)
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(request, form.user)
                # 改动：修改重定向地址
                return HttpResponseRedirect(reverse('%s:app_userinfo_changelist' % self.admin_site.name))
        else:
            form = self.change_password_form(user)

        fieldsets = [(None, {'fields': list(form.base_fields)})]
        adminForm = admin.helpers.AdminForm(form, fieldsets, {})

        context = {
            'title': _('Change password: %s') % escape(user.get_username()),
            'adminForm': adminForm,
            'form_url': form_url,
            'form': form,
            'is_popup': (IS_POPUP_VAR in request.POST or
                         IS_POPUP_VAR in request.GET),
            'add': True,
            'change': False,
            'has_delete_permission': False,
            'has_change_permission': True,
            'has_absolute_url': False,
            'opts': self.model._meta,
            'original': user,
            'save_as': False,
            'show_save': True,
            **self.admin_site.each_context(request),
        }

        request.current_app = self.admin_site.name

        from django.template.response import TemplateResponse
        return TemplateResponse(
            request,
            self.change_user_password_template or
            'admin/auth/user/change_password.html',
            context,
        )


admin.site.unregister(AuthGroup)
