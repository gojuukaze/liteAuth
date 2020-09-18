from django.contrib.auth.password_validation import UserAttributeSimilarityValidator, MinimumLengthValidator
from django.core.exceptions import ValidationError

from lite_auth_http import consts


class UserInfoSimilarityValidator(UserAttributeSimilarityValidator):
    DEFAULT_USER_ATTRIBUTES = ('uid', 'name', 'mail')

    def __init__(self, user_attributes=DEFAULT_USER_ATTRIBUTES, max_similarity=0.7):
        self.user_attributes = user_attributes
        self.max_similarity = max_similarity

    def validate(self, password, user=None):
        if not user:
            return
        user_info = user.user_info
        return super().validate(password, user_info)


class LengthValidator(MinimumLengthValidator):

    def get_help_text(self):
        return '密码长度为 %d-%d' % (self.min_length, consts.MAX_PASSWORD_LENGTH)


class CharacterValidator(object):
    def __init__(self, character_types=2, symbols=r'''!"#$%&'()*+,-./:<=>?@[\]^_`{|}~'''):
        self.character_types = character_types
        self.symbols = symbols

        self.character_types_dict = {}
        self.num = 0

    def add_num(self, i):
        if i in self.character_types_dict:
            return
        self.character_types_dict[i] = 1
        self.num += 1

    def validate(self, password, user=None):

        self.character_types_dict = {}
        self.num = 0

        for c in password:
            if c.isdigit():
                self.add_num(0)
            elif c.islower():
                self.add_num(1)
            elif c.isupper():
                self.add_num(2)
            elif c in self.symbols:
                self.add_num(3)
            else:
                raise ValidationError('包含不允许的符号 ' + c, code='invalid')
            if self.num >= self.character_types:
                return
        raise ValidationError('密码必须包含%d种字符' % self.character_types, code='invalid')

    def get_help_text(self):
        return '密码必须包含%d种字符，允许的标点符号为：%s ' % (self.character_types, self.symbols)


class ReuseValidator(object):
    def __init__(self, num=0):
        self.num = num

    def validate(self, password, user=None):
        if self.num == 0 or not user:
            return

        from lite_auth_http.app.db_manager.password_history import get_password_history_by_uid
        ph = get_password_history_by_uid(user.username)
        if not ph:
            return
        if ph.has(password, self.num):
            raise ValidationError('不能使用近%d次用过的密码' % self.num, code='password_reuse')

    def get_help_text(self):
        return '不能使用近%d次用过的密码' % self.num
