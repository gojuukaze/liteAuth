class BaseLoginError(Exception):
    def __init__(self, message=''):
        self.message = message


class Inactive(BaseLoginError):
    """
    用户不活跃
    """
    pass


class Invalid(BaseLoginError):
    """
    用户名，密码无效
    """

    def __init__(self, message='', login_count=0):
        self.message = message
        self.login_count = login_count  # 连续失败登陆次数


class TooManyLoginAttempts(BaseLoginError):
    pass


class PasswordExpired(BaseLoginError):
    pass
