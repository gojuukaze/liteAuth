from django.conf import settings
from django.core.cache import cache


class BaseBackend(object):

    def __init__(self, **kwargs):
        """
        需要重写
        """
        pass

    def send(self, user, title, msg):
        """
        需要重写
        """
        pass

    """
    这是一个简易的缓存，为了方便有的机器人需要缓存access_token。
    """

    def cache_set(self, key, value, timeout=None):
        """
        :param key:
        :param value:
        :param timeout: 单位秒，None永久保存
        """
        return cache.set(key, value, timeout)

    def cache_get(self, key):
        return cache.get(key)

    def cache_del(self, key):
        return cache.delete(key)

    def send_password_expiration_msg(self, user, days):
        if days > 0:
            self.send(user, 'LiteAuth密码过期', '你的LiteAuth账户（%s）密码将在%d天后过期，请尽快登陆管理后台修改。' % (user.username, days))
        else:
            self.send(user, 'LiteAuth密码过期', '你的LiteAuth账户（%s）密码已过期，账户已限制登陆，在管理后台重置密码后可用。' % user.username)

    def send_login_failure_msg(self, user, login_count):
        if settings.MAX_LOGIN_ATTEMPT_NUM > 3 and settings.MAX_LOGIN_ATTEMPT_NUM - login_count > 3:
            return
        self.send(user, 'LiteAuth密码错误', '你的LiteAuth账户%s登陆密码连续%d次输入错误，连续错误%d次后账户将被锁定。' % (
            user.user_info.uid, login_count, settings.MAX_LOGIN_ATTEMPT_NUM))

    def send_user_locked_msg(self, user):
        self.send(user, 'LiteAuth账户锁定',
                  '你的LiteAuth账户%s因密码连续%d次输入错误已被锁定，账户会在%d秒后自动解锁。' % (
                      user.user_info.uid, settings.MAX_LOGIN_ATTEMPT_NUM, settings.USER_LOCK_DURATION))
