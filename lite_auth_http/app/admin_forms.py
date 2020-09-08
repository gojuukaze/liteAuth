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


class UserAddForm(forms.ModelForm):
    class Meta:
        model = UserInfo
        # exclude = ['is_active', 'try_count', 'last_try_time', 'password_update_date']
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

        user = User(username=user_info.uid, first_name=user_info.name, is_staff=True)
        user._user_info = user_info
        validate_password(password, user)
        user.set_password(self.cleaned_data["password"])

        self.user = user
        return password

    def full_clean(self):
        super().full_clean()
        try:
            self._clean_password()
        except forms.ValidationError as e:
            self.add_error('password', e)
        if self.cleaned_data["reset_password"]:
            d = str_to_date('2019-01-01')
            self.cleaned_data['password_update_date'] = d
            self.instance.password_update_date = d


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
