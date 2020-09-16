from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render

from lite_auth_http.app.db_manager.user import all_user
from lite_auth_http.app.forms import AddAdminForm, AddLdapForm
from lite_auth_http.app.manager.manager import init
from version import version


def init_view(request):
    if all_user().first():
        # 说明已经初始化过了
        return HttpResponseNotFound()

    if request.method == 'POST':
        admin_form = AddAdminForm(request.POST, prefix='创建一个管理员账户')
        ldap_form = AddLdapForm(request.POST, prefix='创建一个LDAP账户')
        # 不能用if and判断，
        # 否则前一个form无效时会导致后一个form没执行is_valid()
        if all([admin_form.is_valid(), ldap_form.is_valid()]):
            init([admin_form, ldap_form])
            return HttpResponseRedirect('/' + settings.ADMIN_URL)
    else:
        admin_form = AddAdminForm(prefix='创建一个管理员账户')
        ldap_form = AddLdapForm(prefix='创建一个LDAP账户')

    admin_form.remove_exclude_field()
    ldap_form.remove_exclude_field()
    forms = [admin_form, ldap_form]

    return render(request, 'app/init.html', {'forms': forms, 'version': version})
