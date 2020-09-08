import requests
from lite_auth_http.notification.base import BaseBackend


class SMS(BaseBackend):
    """
    SMS
    """

    def __init__(self, url, method, json):
        self.url = url
        self.method = method
        self.json = json

    def send(self, user, title, msg):
        data = {'mobile': user.user_info.mobile,
                'msg': '【' + title + '】\n' + msg}
        if self.method.lower() == 'post':
            req = requests.post
            if self.json:
                data = {'json': data}
            else:
                data = {'data': data}
        elif self.method.lower() == 'get':
            req = requests.get
            data = {'params': data}
        else:
            raise RuntimeError('sms backend不支持method： ' + str(self.method))

        req(self.url, **data)
