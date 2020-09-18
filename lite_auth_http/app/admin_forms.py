from django import forms
from django.conf import settings
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth.forms import SetPasswordForm, AdminPasswordChangeForm
from django.contrib.auth.password_validation import password_validators_help_texts, password_validators_help_text_html, \
    get_default_password_validators, validate_password
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.core.validators import RegexValidator
from django.db import transaction
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from lite_auth_http import consts
from lite_auth_http.app import login_exceptions
from lite_auth_http.app.manager.user_manager import confirm_login_allowed
from lite_auth_http.app.models import UserInfo, User
from utils.datetime_helper import str_to_date


class UserAddForm(forms.ModelForm):
    """
    直接新增用户时能用。（一般来说别用这个form，用下面的 UserAddWithGroupsForm ）

    为了兼容admin，这个form保存时先调用save，再调用save_new_user
    如：

    form = UserAddForm()
    if form.is_valid():
        obj = form.save(commit=False)
        form.save_new_user(obj)
    """

    class Meta:
        model = UserInfo
        fields = '__all__'

    password = forms.CharField(label='密码/password', max_length=consts.MAX_PASSWORD_LENGTH,
                               widget=forms.PasswordInput(attrs={'class': 'vTextField'}),
                               help_text='密码，相当于ldap的 userPassword' + str(password_validators_help_text_html()),
                               )
    reset_password = forms.BooleanField(label='重置密码后可用', initial=False, required=False,
                                        help_text='勾选后需要登录管理后台并重置密码后才可用')

    def _clean_password(self):
        password = self.cleaned_data["password"]
        user_info = self.instance

        user = User(username=user_info.uid, first_name=user_info.name, is_staff=True, is_active=True)
        user._user_info = user_info
        validate_password(password, user)
        user.set_password(self.cleaned_data["password"])

        self.user = user
        return password

    def full_clean(self):
        super().full_clean()
        print(self.is_valid())
        if not self.is_bound or (self.empty_permitted and not self.has_changed()):
            return
        if 'password' in self.errors:
            return
        try:
            self._clean_password()
        except forms.ValidationError as e:
            self.add_error('password', e)
        if self.cleaned_data["reset_password"]:
            d = str_to_date('2010-01-01')
            self.cleaned_data['password_update_date'] = d
            self.instance.password_update_date = d

    def save(self, commit=False):
        """
        commit只能为False
        """
        return super(UserAddForm, self).save(False)

    def save_new_user(self, obj):
        with transaction.atomic():
            user = self.user
            user.save()
            obj.is_active = True
            obj.id = user.id
            obj.save()
            from lite_auth_http.app.db_manager.password_history import create_password_history
            create_password_history(obj.uid, password=[user.password])
            return obj


class UserAddWithGroupsForm(UserAddForm):
    class Meta:
        model = UserInfo
        exclude = UserInfo.other_fields()[1:]
        fields = '__all__'

    groups = forms.CharField(max_length=300, initial='', required=False)

    gid_validator = RegexValidator(regex=r'^[\w-]+\Z', message='只允许字母，数字，下划线（_），横杆（-）')

    def clean_groups(self):
        groups = self.cleaned_data['groups']
        if not groups:
            return []
        result = []
        for g in groups.split(','):
            self.gid_validator(g)
            result.append(g)
        return result

    groups_cache = {}

    def get_group(self, gid):
        if gid in self.groups_cache:
            return self.groups_cache[gid]
        from lite_auth_http.app.db_manager.group import get_or_create_group
        g, _ = get_or_create_group(gid)
        self.groups_cache[gid] = g
        return g

    def save(self, commit=True, groups_cache=None):
        """
        commit只能为true
        """
        if groups_cache:
            self.groups_cache = groups_cache
        with transaction.atomic():
            user_info = super(UserAddWithGroupsForm, self).save(False)
            user_info = self.save_new_user(user_info)
            if self.cleaned_data['groups']:
                groups = [self.get_group(g) for g in self.cleaned_data['groups']]
                user_info.groups.set(groups)
        return user_info


class ChangeUserPasswordForm(AdminPasswordChangeForm):
    """
    用于admin用户修改别人的密码
    """

    def save(self, commit=True):
        # commit必须是true，因此这个form不能用于其他地方
        assert commit is True
        password = self.cleaned_data["password1"]
        self.user.set_password(password)
        self.user.save()
        return self.user


class AdminLoginForm(AdminAuthenticationForm):
    error_messages = {
        **AdminAuthenticationForm.error_messages,
        'invalid_login': _(
            "Please enter the correct %(username)s and password for a staff "
            "account. Note that both fields may be case-sensitive."
        ),
    }

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            from lite_auth_http.app.db_manager.user import get_user_by_uid
            user = get_user_by_uid(username)
            if not user:
                raise ValidationError(
                    self.error_messages['inactive'],
                    code='inactive',
                )

            try:
                confirm_login_allowed(user, password, False)
            except login_exceptions.Inactive:
                raise ValidationError(
                    self.error_messages['inactive'],
                    code='inactive',
                )
            except login_exceptions.Invalid:
                raise self.get_invalid_login_error()
            except login_exceptions.TooManyLoginAttempts:
                raise ValidationError('连续失败次数过多，账户已锁定')

            # self.user_cache = authenticate(self.request, username=username, password=password)
            self.user_cache = user

        return self.cleaned_data


class ImportUserForm(forms.Form):
    file = forms.FileField(label='CSV文件')

    max_errors = 10
    warnings = []

    def clean_file(self):
        file = self.cleaned_data.get('file')
        import csv
        try:
            with open(file.temporary_file_path(), 'r')as f:
                r = csv.reader(f)
                _data = list(r)
        except:
            raise ValidationError('无法解析csv文件')

        return self.clean_csv_data(_data)

    def get_msg(self, line, msg):
        return 'row%s : %s' % (str(line), msg)

    def _add_csv_error(self, line, k, err_list):
        for e in err_list:
            self.add_error('file', self.get_msg(line, k + ' : ' + e))

    def clean_csv_data(self, _data):

        err_count = 0
        data = []
        uid, name, password, reset_password, groups, mobile, mail = range(7)
        for line, d in enumerate(_data[1:]):
            line += 2
            d = [i.strip() for i in d]
            if not d[uid]:
                self.warnings.append(self.get_msg(line, 'uid为空，忽略该行'))
                continue

            f = UserAddWithGroupsForm({'uid': d[uid],
                                       'name': d[name],
                                       'password': d[password],
                                       'reset_password': int(d[reset_password]),
                                       'groups': d[groups],
                                       'mobile': d[mobile],
                                       'mail': d[mail]})
            if f.is_valid() and err_count == 0:
                data.append(f)
            else:
                for k, es in f.errors.items():
                    self._add_csv_error(line, k, es)
                    err_count += len(es)
            # 错误太多就不监测了
            if err_count >= self.max_errors:
                return
        return data
