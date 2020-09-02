import json
from urllib.parse import urljoin

from ldaptor.protocols.ldap import ldaperrors

from config import LDAP_API_URL
from lite_auth_ldap.manager import json_post, filter_object_to_str
from lite_auth_ldap.model import User


# def request_err(e):
#     print(e)
#     raise ldaperrors.LDAPOther('HttpServerNeverReceived')


def request_success(resp, callback, *callback_args):
    def do(data):
        code = data['code']
        if code != 0:
            raise ldaperrors.reverse[code](data['msg'])
        return callback(data, resp, *callback_args)

    if resp.code != 200:
        raise ldaperrors.LDAPOther('Http server return ' + str(resp.code))

    d = resp.json()
    d.addCallback(do)
    return d


class LiteAuthHandler(object):

    def post(self, url, data, cookies, callback, *callback_args):
        d = json_post(url, data, cookies)
        d.addCallback(request_success, callback, *callback_args)
        # d.addCallback(callback, *callback_args)
        # d.addErrback(request_err)
        return d

    def _bind(self, data, resp):
        user = User(data['data'])
        return resp.cookies(), user

    def bind(self, dn, password):
        url = urljoin(LDAP_API_URL, '/ldap/bind')
        data = {'dn': dn, 'password': password}

        return self.post(url, data, None, self._bind)

    def _search(self, data, resp, callback):
        data = data['data']
        for u in data['users']:
            callback(User(u))
        return data['controls']

    def search(self, cookies, filter_obj, attributes, controls, callback):
        url = urljoin(LDAP_API_URL, '/ldap/search')
        data = {'attributes': attributes,
                'filter_text': filter_object_to_str(filter_obj),
                'controls': controls
                }
        return self.post(url, data, cookies, self._search, callback)
        # d = json_post(url, data, cookies)
        # d.addCallback(self._search, callback)
        # d.addErrback(request_err)
        # 
        # return d
