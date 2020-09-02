from django.urls import path

from lite_auth_http.ldap_api import views

urlpatterns = [
    path('bind', views.bind_view),
    path('search', views.search_view),

]
