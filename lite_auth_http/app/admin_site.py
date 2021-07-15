import io
from functools import update_wrapper

from django.contrib import messages
from django.contrib.admin import AdminSite
from django.contrib.auth import REDIRECT_FIELD_NAME, logout
from django.http import HttpResponse, HttpResponseBadRequest, FileResponse
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt

from lite_auth_http.app.admin_actions import delete_selected
from lite_auth_http.app.admin_forms import AdminLoginForm, ImportUserForm


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

    password_change_template='admin_ex/password_change_form.html'
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
        from lite_auth_http.app.admin_views import UserPasswordChangeView
        return UserPasswordChangeView.as_view(**defaults)(request)

    def get_urls(self):

        urlpatterns = super(LiteAuthAdminSite, self).get_urls()

        def wrap(view, cacheable=False):
            def wrapper(*args, **kwargs):
                return self.admin_view(view, cacheable)(*args, **kwargs)

            wrapper.admin_site = self
            return update_wrapper(wrapper, view)

        from django.urls import path
        urlpatterns = [path('import_user/', wrap(self.import_user), name='import_user'),
                       path('demo.csv', wrap(self.csv_demo), name='csv_demo'),
                       ] + urlpatterns

        return urlpatterns

    def csv_demo(self, request, extra_context=None):
        if request.user.is_anonymous or not request.user.is_admin():
            return HttpResponseBadRequest()
        csv = b'uid,name,password,\xe9\x87\x8d\xe7\xbd\xae\xe5\xaf\x86\xe7\xa0\x81\xe5\x90\x8e\xe5\x8f\xaf\xe7\x94' \
              b'\xa8\xef\xbc\x880:false; 1:true\xef\xbc\x89,' \
              b'groups\xef\xbc\x88\xe7\x94\xa8\xe9\x80\x97\xe5\x8f\xb7\xe5\x88\x86\xe9\x9a\x94\xef\xbc\x8c\xe4\xb8' \
              b'\x8d\xe5\xad\x98\xe5\x9c\xa8\xe7\x9a\x84\xe7\xbb\x84\xe4\xbc\x9a\xe8\x87\xaa\xe5\x8a\xa8\xe5\x88\x9b' \
              b'\xe5\xbb\xba\xef\xbc\x89,mobile,mail\r\nuser1,username,secert,1,"admin,group1",,\r\n '

        buffer = io.BytesIO(csv)
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='demo.csv')

    @csrf_exempt
    def import_user(self, request, extra_context=None):
        if request.user.is_anonymous or not request.user.is_admin():
            return HttpResponseBadRequest()

        context = {
            'extra_context': {**self.each_context(request), **(extra_context or {})},
            'title': '从CSV导入用户',

        }
        context.update(extra_context or {})

        defaults = {
            'extra_context': context,
            'template_name': 'admin_ex/import_user.html',
            'form_class': ImportUserForm,
            'success_url': reverse('admin:import_user', current_app=self.name)
        }
        request.current_app = self.name

        from lite_auth_http.app.admin_views import ImportUserView
        return ImportUserView.as_view(**defaults)(request)
