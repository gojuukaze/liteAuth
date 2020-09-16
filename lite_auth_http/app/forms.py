from django import forms
from django.conf import settings

from lite_auth_http.app.admin_forms import UserAddWithGroupsForm
from lite_auth_http.app.models import UserInfo


class InitBaseForm(UserAddWithGroupsForm):
    class Meta:
        model = UserInfo
        fields = ['uid', 'name', ]

    _remove_field = ['reset_password', 'groups']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for k, v in self.fields.items():
            v.widget.attrs.update({'class': 'input'})

    def clean_reset_password(self):
        return False

    def clean_groups(self):
        return []

    def remove_exclude_field(self):
        for f in self._remove_field:
            self.fields.pop(f)


class AddAdminForm(InitBaseForm):

    def clean_groups(self):
        return ['admin']


class AddLdapForm(InitBaseForm):
    uid = forms.CharField(label='用户名/uid', initial=settings.LDAP_USER, help_text='只支持在配置文件中修改', disabled=True,
                          show_hidden_initial=True)
    name = forms.CharField(initial=settings.LDAP_USER, disabled=True, widget=forms.HiddenInput())

    def clean_name(self):
        return settings.LDAP_USER
