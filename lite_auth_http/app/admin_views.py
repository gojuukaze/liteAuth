from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView
from django.core.files.uploadhandler import TemporaryFileUploadHandler
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.generic import FormView

from lite_auth_http.app.admin_forms import ImportUserForm
from utils.datetime_helper import str_to_date


class UserPasswordChangeView(PasswordChangeView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        _from = self.request.GET.get('from')
        if _from == 'reset':
            context['title'] = '密码已过期，请重置密码'

        return context

    def form_valid(self, form):
        with transaction.atomic():
            form.save()
        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(self.request, form.user)
        return FormView.form_valid(self, form)


class ImportUserView(FormView):

    def post(self, request, *args, **kwargs):
        request.upload_handlers = [TemporaryFileUploadHandler(request)]
        return self._post(request, *args, **kwargs)

    @method_decorator(csrf_protect)
    def _post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    group_dict = {}

    def get_group(self, gid):
        if gid in self.group_dict:
            return self.group_dict[gid]
        from lite_auth_http.app.db_manager.group import get_or_create_group
        g, _ = get_or_create_group(gid)
        self.group_dict[gid] = g
        return g

    def form_valid(self, form):
        data = form.cleaned_data['file']
        from lite_auth_http.app.manager.user_manager import new_user
        line = 0
        from lite_auth_http.app.models import User
        try:
            with transaction.atomic():
                for i, add_form in enumerate(data):
                    line = i + 2
                    for gid in add_form.cleaned_data['groups']:
                        self.get_group(gid)
                    add_form.save(groups_cache=self.group_dict)
        except BaseException as e:
            messages.add_message(self.request, messages.ERROR, 'row' + str(line) + ': ' + str(e))
            return self.form_invalid(form)
        else:
            messages.add_message(self.request, messages.SUCCESS, '导入完成')
            for w in form.warnings:
                messages.add_message(self.request, messages.WARNING, w)

        return super(ImportUserView, self).form_valid(form)
