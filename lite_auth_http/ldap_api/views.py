import time

from django.conf import settings
from django.contrib.auth import login
from django.shortcuts import render

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from ldaptor.protocols.ldap import ldaperrors

from lite_auth_http.ldap_api.manager import search, bind
from lite_auth_http.utils.auth import ldap_login_required
from lite_auth_http.utils.json_post import json_post
from lite_auth_http.utils.response import json_response


@csrf_exempt
@json_post()
def bind_view(request):
    dn = request.POST.get('dn')
    password = request.POST.get('password')

    if not dn or not password:
        return json_response(code=ldaperrors.LDAPInvalidDNSyntax.resultCode)

    try:
        user, user_info = bind(dn, password)
    except ldaperrors.LDAPException as e:
        return json_response(code=e.resultCode, msg=str(e))

    login(request, user)
    request.session.set_expiry(settings.LDAP_API_AUTH_EXPIRY)
    return json_response(data=user_info)


@csrf_exempt
@ldap_login_required()
@json_post()
def search_view(request):
    user = request.user
    filter_text = request.POST.get('filter_text')
    attributes = request.POST.get('attributes')
    controls = request.POST.get('controls')

    if not filter_text:
        return json_response(data=[])
    if '*' in attributes:
        attributes = None
    try:
        data, controls = search(user, filter_text, attributes, controls)
        return json_response(data={'users': data, 'controls': controls})

    except ldaperrors.LDAPException as e:
        return json_response(code=e.resultCode, msg=str(e))
