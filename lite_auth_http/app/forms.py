from django import forms
from django.conf import settings
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth.forms import SetPasswordForm, AdminPasswordChangeForm
from django.contrib.auth.password_validation import password_validators_help_texts, password_validators_help_text_html, \
    get_default_password_validators, validate_password
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from lite_auth_http import consts
from lite_auth_http.app import login_exceptions
from lite_auth_http.app.manager.user_manager import confirm_login_allowed
from lite_auth_http.app.models import UserInfo, User
from utils.datetime_helper import str_to_date


class InitForm(forms.ModelForm):
    class Meta:
        attrs = {'class': 'input'}

        model = UserInfo
        fields = ['uid', 'name']
        widgets = {
            'uid': forms.TextInput(attrs=attrs),
            'name': forms.TextInput(attrs=attrs)

        }
        labels = {
            'uid': '管理员用户名/uid',
            'name': '管理员姓名/name'
        }

    password = forms.CharField(label='管理员密码/password', max_length=consts.MAX_PASSWORD_LENGTH,
                               help_text='密码，相当于ldap的 userPassword<br>初始化时不进行密码校验',
                               widget=forms.PasswordInput(attrs=Meta.attrs)
                               )

    ldap_uid = forms.CharField(label='LDAP用户名', initial=settings.LDAP_USER, help_text='只支持在配置文件中修改', disabled=True,
                               widget= forms.TextInput(attrs=Meta.attrs))
    ldap_password = forms.CharField(label='LDAP用户密码', max_length=consts.MAX_PASSWORD_LENGTH,
                                    help_text='密码，相当于ldap的 userPassword<br>初始化时不进行密码校验',
                                    widget=forms.PasswordInput(attrs=Meta.attrs)
                                    )

    def clean_password(self):
        password = self.cleaned_data["password"]

        user = User(username=self.cleaned_data['uid'], first_name=self.cleaned_data['name'], is_staff=True)
        validate_password(password, user)
        return password

    # def full_clean(self):
    #     super().full_clean()
    #     try:
    #         self._clean_password()
    #     except forms.ValidationError as e:
    #         self.add_error('password', e)


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
