from django.conf import settings
from django.contrib import admin
from django.urls import path, include

from lite_auth_http.app.views import init_view

urlpatterns = [
    path('', init_view),

]
