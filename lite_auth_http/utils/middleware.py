from urllib.parse import urljoin

from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse


def password_age_middleware(get_response):
    """
    登录admin时，校验密码有效期
    """

    def middleware(request):
        password_change_url=reverse('admin:password_change')
        if request.path.startswith(urljoin('/', settings.ADMIN_URL)) \
                and not request.path.startswith(password_change_url) \
                and request.user.is_authenticated \
                and request.user.user_info.is_password_expired():
            return HttpResponseRedirect(password_change_url + '?from=reset')

        return get_response(request)

    return middleware
