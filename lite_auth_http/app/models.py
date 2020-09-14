from django import forms
from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from jsonfield.fields import JSONField
from lite_auth_http import consts
from utils.datetime_helper import now, get_today_date


class User(AbstractUser):

    @property
    def user_info(self):
        if getattr(self, '_user_info', 0) == 0:
            from lite_auth_http.app.db_manager.user_info import get_user_info_by_uid
            self._user_info = get_user_info_by_uid(self.username)
            self._user_info._user = self
        return self._user_info

    def has_group(self, gid):
        return self.user_info.has_group(gid)

    def is_admin(self):
        return self.has_group(consts.ADMIN_GROUP)

    def is_ldap_user(self):
        return self.username == settings.LDAP_USER

    def get_full_name(self):
        return self.user_info.name

    def get_short_name(self):
        return self.user_info.name

    def set_password(self, raw_password):
        super().set_password(raw_password)
        # 没有id，说明是创建用户
        if self.id:
            user_info = self.user_info
            user_info.password_update_date = get_today_date()
            user_info.save()
            user_info.password_history.add_password(self.password)


class UserInfo(models.Model):
    class Meta:
        verbose_name_plural = '用户'
        verbose_name = '用户'

    uid_validator = RegexValidator(regex=r'^[\w-]+\Z', message='uid只允许字母，数字，下划线（_），横杆（-）')
    uid = models.CharField('用户名/uid', max_length=50, unique=True,
                           help_text='用户的登录名，相当于ldap的 cn/uid/sn<br>「 %s 」' % uid_validator.message,
                           validators=[uid_validator])
    # ---- 属性字段 ------
    name = models.CharField('姓名/name', max_length=50, help_text='名字，相当于ldap的 givenName。一般填中文名')

    mail = models.CharField('邮箱/mail', max_length=100, help_text='电子邮箱，相当于ldap的 mail', default='', blank=True)
    mobile = models.CharField('手机/mobile', max_length=100, help_text='手机，相当于ldap的 mobile', default='', blank=True)
    ssh_key = models.TextField('公钥/ssh_key', help_text='公钥', default='', blank=True)

    # ---- 属性字段 end ------

    is_active = models.BooleanField('激活', default=True, help_text='激活才允许登录')

    try_count = models.IntegerField('尝试登录次数', default=0, blank=True, help_text='只有管理员才能修改')
    last_try_time = models.DateTimeField('上次登录失败时间', null=True, blank=True)

    password_never_expire = models.BooleanField('用户密码永不过期', default=False)
    password_update_date = models.DateField('上次修改密码日期', default=now, blank=True)

    def __str__(self):
        return '%s(%s)' % (self.uid, self.name)

    @property
    def user(self):
        if getattr(self, '_user', 0) == 0:
            from lite_auth_http.app.db_manager.user import get_user_by_uid
            self._user = get_user_by_uid(self.uid)
            self._user._user_info = self
        return self._user

    @property
    def password_history(self):
        if getattr(self, '_password_history', 0) == 0:
            from lite_auth_http.app.db_manager.password_history import get_password_history_by_uid
            self._password_history = get_password_history_by_uid(self.uid)
        return self._password_history

    @classmethod
    def attrs_fields(cls):
        return ['name', 'mail', 'mobile', 'ssh_key']

    @classmethod
    def other_fields(cls):
        # uid必须是第一个
        return ['uid', 'is_active', 'try_count', 'last_try_time', 'password_update_date', 'password_never_expire']

    def has_group(self, gid):
        return self.groups.filter(gid=gid).exists()

    def is_admin(self):
        return self.has_group(consts.ADMIN_GROUP)

    def is_ldap_user(self):
        return self.uid == settings.LDAP_USER

    def is_password_expired(self):
        if self.password_never_expire:
            return False
        return (get_today_date() - self.password_update_date).days > settings.MAX_PASSWORD_AGE

    def reset_lock(self):
        """
        重置锁
        """
        self.try_count = 0
        self.last_try_time = None
        self.save()

    def add_try_count(self):
        self.try_count += 1
        self.last_try_time = now()
        self.save()

    def is_lock(self):
        if settings.MAX_LOGIN_ATTEMPT_NUM == 0:
            return False
        if self.try_count >= settings.MAX_LOGIN_ATTEMPT_NUM:
            if (now() - self.last_try_time).seconds > settings.USER_LOCK_DURATION:
                self.reset_lock()
                return False
            else:
                return True
        else:
            if self.try_count > 0 and (now() - self.last_try_time).seconds > settings.RESET_LOGIN_ATTEMPT_NUM_AFTER:
                self.reset_lock()
            return False


class Group(models.Model):
    class Meta:
        verbose_name_plural = '组'

    gid_validator = RegexValidator(regex=r'^[\w-]+\Z', message='gid只允许字母，数字，下划线（_），横杆（-）')

    gid = models.CharField('组名/gid', max_length=30, unique=True, validators=[gid_validator])
    desc = models.TextField('描述', default='', blank=True)

    users = models.ManyToManyField(
        UserInfo,
        verbose_name='users',
        related_name='groups',
        blank=True,
        db_table='app_group_userinfo'
    )

    def __str__(self):
        return self.gid


class PasswordHistory(models.Model):
    uid = models.CharField('用户名', max_length=50, unique=True)
    password = JSONField('password', default=[])

    def add_password(self, password):
        if len(self.password) == consts.MAX_PASSWORD_HISTORY:
            self.password.pop()
        self.password.insert(0, password)
        self.save()

    def has(self, raw_password, n):
        from django.contrib.auth.hashers import check_password
        for p in self.password[:n]:
            if check_password(raw_password, p):
                return True
        return False
