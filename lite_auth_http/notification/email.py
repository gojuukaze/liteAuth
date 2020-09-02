from django.core import mail
from django.core.mail import send_mail

from lite_auth_http.notification.base import BaseBackend


class Email(BaseBackend):
    """
    email
    需要登录飞书开放平台后创建企业自建应用，打开机器人功能并给予权限
    """

    def __init__(self, host, port, username, password, use_tls=False, use_ssl=False,
                 ssl_keyfile=None, ssl_certfile=None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.use_ssl = use_ssl
        self.ssl_keyfile = ssl_keyfile
        self.ssl_certfile = ssl_certfile

    def send(self, user, title, msg):
        with mail.get_connection(host=self.host, port=self.port, username=self.username, password=self.password,
                                 use_tls=self.use_tls, use_ssl=self.use_ssl,
                                 ssl_keyfile=self.ssl_keyfile, ssl_certfile=self.ssl_certfile) as connection:
            send_mail(title, msg, self.username, [user.user_info.mail], connection=connection)
