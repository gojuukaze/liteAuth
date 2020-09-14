from django.conf import settings
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('', include('lite_auth_http.app.urls')),

    path(settings.ADMIN_URL, admin.site.urls),
    path('ldap/', include('lite_auth_http.ldap_api.urls')),
]
