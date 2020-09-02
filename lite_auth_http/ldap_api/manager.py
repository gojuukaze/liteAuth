from itertools import chain

from django.conf import settings
from ldaptor import ldapfilter
from ldaptor.protocols.ldap import ldaperrors

from lite_auth_http.app import login_exceptions
from lite_auth_http.app.db_manager.user import get_user_by_uid
from lite_auth_http.app.manager.user_manager import confirm_login_allowed
from lite_auth_http.app.models import UserInfo
from lite_auth_http.ldap_api.ldap_manager import ldap_dn_to_dict, filter_text_to_query
from lite_auth_http.ldap_api.page_control import PagedResultsControl
from utils.datetime_helper import get_today, get_today_date


def user_info_model_to_dict(user_info, exclude):
    opts = user_info._meta
    data = {}
    for f in chain(opts.concrete_fields, opts.private_fields):
        if f.name in exclude:
            continue
        k = settings.LITE_AUTH_FIELD_MAP.get(f.name, f.name)

        data[k] = [f.value_from_object(user_info)]
    return data


def get_user_info_dict(user_info, attributes=None, exclude=None):
    """

    :param user_info:
    :param attributes: None表示未设置attributes，即返回所有attributes
    :param exclude:
    :return:
    """
    if exclude is None:
        exclude = ['id'] + UserInfo.other_fields()[1:]

    d = user_info_model_to_dict(user_info, exclude)

    result = {}

    dn_k = settings.LITE_AUTH_FIELD_MAP.get('uid', 'uid')
    result['dn'] = dn_k + '=' + user_info.uid

    if attributes:
        for k in attributes:
            result[k] = d.get(k, [])
    else:
        result.update(d)

    if attributes is None or 'groups' in attributes:
        result['groups'] = list(user_info.groups.values_list('gid', flat=True))

    return result


"""
raise的错误说明参考：https://ldapwiki.com/wiki/LDAP%20Result%20Codes
"""


def bind(dn, password):
    query = ldap_dn_to_dict(dn)
    uid = query.get('uid', '')

    user = get_user_by_uid(uid)
    if not user:
        raise ldaperrors.LDAPNoSuchObject(dn)

    # user_info = user.user_info
    # 
    # if not user_info.is_active:
    #     raise ldaperrors.LDAPNoSuchObject(dn)
    # if not user.check_password(password):
    #     user_info.add_try_count()
    #     raise ldaperrors.LDAPInvalidCredentials()
    # 
    # if user_info.is_lock():
    #     raise ldaperrors.LDAPInvalidCredentials('tooManyLoginAttempts')
    # if user_info.is_password_expired():
    #     raise ldaperrors.LDAPInvalidCredentials('passwordExpired')
    try:
        confirm_login_allowed(user, password)
    except login_exceptions.Inactive:
        raise ldaperrors.LDAPNoSuchObject(dn)
    except login_exceptions.Invalid:
        raise ldaperrors.LDAPInvalidCredentials()
    except login_exceptions.TooManyLoginAttempts:
        raise ldaperrors.LDAPInvalidCredentials('tooManyLoginAttempts')
    except login_exceptions.PasswordExpired:
        raise ldaperrors.LDAPInvalidCredentials('passwordExpired')

    return user, get_user_info_dict(user.user_info, attributes=[])


def get_controls(controls):
    for control_type, criticality, control_value in controls:
        if control_type == PagedResultsControl.control_type:
            return [PagedResultsControl.fromBER(criticality, control_value)]
        elif criticality:
            raise ldaperrors.LDAPUnavailableCriticalExtension('Unknown control %s' % control_type)
    return []


def search(user, filter_text, attributes, controls):
    controls = get_controls(controls)
    if controls:
        pg_ctl = controls[0]
    else:
        pg_ctl = None

    if attributes:
        attributes = [k.lower() for k in attributes]

    query = filter_text_to_query(filter_text)
    if not user.is_admin() and not user.is_ldap_user():
        query = query.filter(uid=user.username)

    query.filter(is_active=True).order_by('id')

    if pg_ctl:
        if pg_ctl.remain_count is None:
            pg_ctl.remain_count = query.count()
        user_info = query.filter(id__gt=pg_ctl.last_id)[:min(pg_ctl.size, settings.SEARCH_LIMIT)]
    else:
        user_info = query[:settings.SEARCH_LIMIT]
    user_info = list(user_info)

    result = []
    for u in user_info:
        result.append(get_user_info_dict(u, attributes))

    if pg_ctl:
        pg_ctl.last_id = user_info[-1].id
        pg_ctl.remain_count -= len(user_info)
        return result, [pg_ctl.ctl]
    return result, []
