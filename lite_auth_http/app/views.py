from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render

from lite_auth_http.app.db_manager.user import all_user
from lite_auth_http.app.forms import InitForm
from lite_auth_http.app.manager.manager import init
from version import version


def init_view(request):
    if request.method == 'POST':
        form = InitForm(request.POST)
        if form.is_valid():
            init(form.cleaned_data)
            return HttpResponseRedirect(settings.ADMIN_URL)
    else:
        if all_user().first():
            # 说明已经初始化过了
            return HttpResponseNotFound()
        form = InitForm()
    form = list(form)
    new_form = [{'title': '创建一个管理员账户', 'form': form[:3]}, {'title': '创建一个LDAP账户', 'form': form[3:]}]
    return render(request, 'app/init.html', {'new_form': new_form, 'version': version})
