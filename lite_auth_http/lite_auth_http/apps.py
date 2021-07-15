# django3.2 自定义的admin需放到这

from django.contrib.admin.apps import AdminConfig


class LiteAuthAdminConfig(AdminConfig):
    default_site = 'lite_auth_http.app.admin_site.LiteAuthAdminSite'

