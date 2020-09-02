from django.conf import settings
from django.db.models import Q
from ldaptor import ldapfilter
from ldaptor.protocols import pureldap
from ldaptor.protocols.ldap import ldapsyntax, ldaperrors

from lite_auth_http.app.models import UserInfo


def ldap_dn_to_dict(dn):
    query = {}
    for a in dn.split(','):
        k, v = a.split('=')
        k = k.strip()
        v = v.strip()
        if k == 'dc':
            continue
        k = settings.LDAP_FIELD_MAP.get(k, k)
        query[k] = v
    return query


def get_k_v_from_filter_obj(f):
    if isinstance(f, pureldap.LDAPAttributeValueAssertion):
        k = f.attributeDesc.value.lower()
        v = f.assertionValue.value
    elif isinstance(f, pureldap.LDAPFilter_substrings):
        k = f.type.lower()
        v = ''
    else:
        raise NotImplementedError('Filter type not supported %r' % f)
    k = settings.LDAP_FIELD_MAP.get(k, k)
    # 搜索的条件不存在，且值也不为*，则返回 (id,-1) 防止orm报错
    if k not in UserInfo.attrs_fields() + UserInfo.other_fields() and v != '*':
        return 'id', -1

    if k == 'groups':
        k = 'groups__gid'

    return k, v


def filter_obj_to_tree(f):
    tree = Q()
    if isinstance(f, pureldap.LDAPFilter_present):
        pass
    elif isinstance(f, pureldap.LDAPFilter_equalityMatch):
        k, v = get_k_v_from_filter_obj(f)
        if v != '*':
            tree = Q(**{k: v})

    elif isinstance(f, pureldap.LDAPFilter_greaterOrEqual):
        k, v = get_k_v_from_filter_obj(f)
        tree = Q(**{k + '__gte': v})
    elif isinstance(f, pureldap.LDAPFilter_lessOrEqual):
        k, v = get_k_v_from_filter_obj(f)
        tree = Q(**{k + '__lte': v})
    elif isinstance(f, pureldap.LDAPFilter_not):
        tree = ~filter_obj_to_tree(f.value)
    elif isinstance(f, pureldap.LDAPFilter_substrings):
        k, _ = get_k_v_from_filter_obj(f)
        for sub in f.substrings:
            if isinstance(sub, pureldap.LDAPFilter_substrings_initial):
                tree &= Q(**{k + '__startswith': sub.value})
            elif isinstance(sub, pureldap.LDAPFilter_substrings_final):
                tree &= Q(**{k + '__endswith': sub.value})
            elif isinstance(sub, pureldap.LDAPFilter_substrings_any):
                tree &= Q(**{k + '__contains': sub.value})
            else:
                return None
    else:
        if isinstance(f, pureldap.LDAPFilter_and):
            for filt in f:
                tree &= filter_obj_to_tree(filt)
        elif isinstance(f, pureldap.LDAPFilter_or):
            for filt in f:
                tree |= filter_obj_to_tree(filt)
        else:
            return None
    return tree


def filter_text_to_query(filter_text):
    filter_text = filter_text.replace(' ', '')
    tree = filter_obj_to_tree(ldapfilter.parseFilter(filter_text))
    if not tree:
        raise ldaperrors.LDAPInappropriateMatching(filter_text)
    return UserInfo.objects.filter(tree)
