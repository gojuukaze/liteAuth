import json

import treq
from ldaptor.protocols import pureldap
from ldaptor.protocols.ldap import ldapsyntax
from requests.cookies import RequestsCookieJar

from config import LDAP_API_TIMEOUT
from utils.json_encoder import LiteAuthJsonEncoder


def json_post(url, data, cookies=None):
    if cookies is None:
        cookies = {}
    if isinstance(cookies, RequestsCookieJar):
        jar = cookies
    else:
        jar = RequestsCookieJar()
        for k, v in cookies.items():
            jar.set_cookie(k, v)
    return treq.post(url, json.dumps(data, cls=LiteAuthJsonEncoder).encode('ascii'),
                     headers={b'Content-Type': [b'application/json']},
                     cookies=jar, timeout=LDAP_API_TIMEOUT)


def get(url, params):
    return treq.get(url, params=params, timeout=LDAP_API_TIMEOUT)


def to_str(s):
    if isinstance(s, str):
        return s
    if isinstance(s, bytes):
        return str(s, encoding='utf-8')


def filter_object_to_str(f):
    s = ''
    if isinstance(f, pureldap.LDAPFilter_present):
        s = '(%s=*)' % to_str(f.value)
    elif isinstance(f, pureldap.LDAPFilter_equalityMatch):
        s = " (%s=%s)" % (to_str(f.attributeDesc.value), to_str(f.assertionValue.value))
    elif isinstance(f, pureldap.LDAPFilter_greaterOrEqual):
        s = " (%s>=%s)" % (to_str(f.attributeDesc.value), to_str(f.assertionValue.value))
    elif isinstance(f, pureldap.LDAPFilter_lessOrEqual):
        s = "(%s<=%s)" % (to_str(f.attributeDesc.value), to_str(f.assertionValue.value))
    elif isinstance(f, pureldap.LDAPFilter_not):
        s = filter_object_to_str(f.value)
        s = ' (!%s)' % s
    elif isinstance(f, pureldap.LDAPFilter_substrings):
        initial = ''
        final = ''
        any = []
        for sub in f.substrings:
            if isinstance(sub, pureldap.LDAPFilter_substrings_initial):
                initial = to_str(sub.value)
            elif isinstance(sub, pureldap.LDAPFilter_substrings_final):
                final = to_str(sub.value)
            elif isinstance(sub, pureldap.LDAPFilter_substrings_any):
                any.append(to_str(sub.value))
            else:
                raise NotImplementedError('Filter type not supported %r' % sub)
        s = "(%s=%s)" % (to_str(f.type), '*'.join([initial] + any + [final]))
    else:
        s = []
        for filt in f:
            s.append(filter_object_to_str(filt))
        if isinstance(f, pureldap.LDAPFilter_and):
            s = '(&%s)' % ''.join(s)
        elif isinstance(f, pureldap.LDAPFilter_or):
            s = '(|%s) ' % ''.join(s)
        else:
            raise ldapsyntax.MatchNotImplemented(f)
    return s
