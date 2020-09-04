from django.contrib.auth.views import PasswordChangeView
# Create your views here.
from django.db import transaction
from django.views.generic import FormView

from utils.datetime_helper import get_today_date


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
