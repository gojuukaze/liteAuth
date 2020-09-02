import requests

from lite_auth_http.notification.base import BaseBackend


class FeiShu(BaseBackend):
    """
    飞书机器人
    需要登录飞书开放平台后创建【企业自建应用】，打开机器人功能并给予权限
    """

    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret

    def get_token(self):
        token = self.cache_get('token')
        if not token:
            r = requests.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/',
                              json={'app_id': self.app_id, 'app_secret': self.app_secret})
            data = r.json()
            if data['code'] != 0:
                raise RuntimeError('飞书机器人获取token失败 %s' % r.text)
            token = data['tenant_access_token']
            self.cache_set('token', token, data['expire'] - 100)
        return token

    def get_feishu_user_id(self, user):

        r = requests.get('https://open.feishu.cn/open-apis/user/v1/batch_get_id',
                         params={'mobiles': user.user_info.mobile},
                         headers={'Authorization': 'Bearer %s' % self.get_token()}
                         )
        data = r.json()
        if data['code'] != 0:
            raise RuntimeError('飞书机器人获取user失败 %s' % r.text)
        return data['data']['mobile_users'][user.user_info.mobile][0]['user_id']

    def send(self, user, title, msg):

        user_id = self.get_feishu_user_id(user)
        requests.post('https://open.feishu.cn/open-apis/message/v4/send/',
                      json={'user_id': user_id, 'msg_type': 'text',
                            'content': {'text': '【' + title + '】\n' + msg}},
                      headers={'Authorization': 'Bearer %s' % self.get_token()}
                      )
