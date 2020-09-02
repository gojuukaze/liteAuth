from django.apps import AppConfig
from django.contrib.admin.apps import AdminConfig


class MAppConfig(AppConfig):
    name = 'app'

class LiteAuthAdminConfig(AdminConfig):
    default_site = 'lite_auth_http.app.admin_site.LiteAuthAdminSite'

    def ready(self):
        super().ready()
        self.module.autodiscover()


