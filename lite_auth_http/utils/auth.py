from functools import wraps


def ldap_login_required():
    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                from ldaptor.protocols.ldap import ldaperrors
                from lite_auth_http.utils.response import json_response
                return json_response(code=ldaperrors.LDAPInsufficientAccessRights().resultCode)
            else:
                return func(request, *args, **kwargs)

        return inner

    return decorator
