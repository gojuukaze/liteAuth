from django.apps import AppConfig
from django.contrib.admin.apps import AdminConfig


class MAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'

    # 升级django3.2后，由于manage.py和django项目不在同一层，name前面需要加上lite_auth_http
    name = 'lite_auth_http.app'

