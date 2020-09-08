from functools import update_wrapper

from django.contrib import admin
from django.contrib.admin.sites import all_sites
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _, gettext_lazy

from django.contrib.admin import AdminSite
from django.contrib.auth import REDIRECT_FIELD_NAME, logout
from django.http import HttpResponse
from django.urls import reverse
from django.views.decorators.cache import never_cache

from lite_auth_http.app.admin_actions import delete_selected
from lite_auth_http.app.admin_forms import AdminLoginForm


class LiteAuthAdminSite(AdminSite):
    site_header = 'Lite Auth后台管理'
    name = 'Lite Auth后台管理'
    site_title = 'Lite Auth后台管理'
    index_title = 'Lite Auth后台管理'
    enable_nav_sidebar = False
    login_form = AdminLoginForm

    def has_permission(self, request):
        if request.user.is_anonymous:
            return False
        return request.user.user_info.is_active and not request.user.is_ldap_user()

    def password_change(self, request, extra_context=None):
        from django.contrib.admin.forms import AdminPasswordChangeForm
        url = reverse('admin:password_change_done', current_app=self.name)
        defaults = {
            'form_class': AdminPasswordChangeForm,
            'success_url': url,
            'extra_context': {**self.each_context(request), **(extra_context or {})},
        }
        if self.password_change_template is not None:
            defaults['template_name'] = self.password_change_template
        request.current_app = self.name
        # 改动: 修改了使用的view
        from lite_auth_http.app.views import UserPasswordChangeView
        return UserPasswordChangeView.as_view(**defaults)(request)

    def get_urls(self):

        urlpatterns = super(LiteAuthAdminSite, self).get_urls()

        def wrap(view, cacheable=False):
            def wrapper(*args, **kwargs):
                return self.admin_view(view, cacheable)(*args, **kwargs)

            wrapper.admin_site = self
            return update_wrapper(wrapper, view)

        from django.urls import path
        urlpatterns += [path('import_user/', wrap(self.import_user), name='import_user'),
                        ]

        return urlpatterns

    def import_user(self, request, extra_context=None):
        if not request.user.is_admin():
            return HttpResponse('<h1>无权限</h1>',status=400)

        return HttpResponse('<h1>待开发</h1>')
