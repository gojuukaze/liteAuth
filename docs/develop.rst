***************
开发指南
***************

如果你是从源码安装，你的代码应该放在源码目录的 ``custom`` 下。

如果你是从docker安装，你需要新建目录 ``custom`` 并在启动时添加参数 ``-v /your_path/custom:/app/liteauth/custom``

.. _custom_notification_backend:

自定义通知backend
========================

1. 创建文件 ``custom/my_backend.py`` ，
编写你的类继承 ``BaseBackend`` 并实现 ``__init__`` , ``send`` 方法

   .. code-block:: python
      :caption: my_backend.py

      class MyBackend(BaseBackend):

          def __init__(self, data):
              """
              指定初始化的参数，这个参数会从配置文件中传入
              """
              self.data = data

          def send(self, user, title, msg):
              """
              :param user: User类，其定义在lite_auth_http/app/models.py下 。
                           user.user_info用户信息，UserInfo类，同样也定义在lite_auth_http/app/models.py下 。
              :param title:
              :param msg:
              """
              mobile = user.user_info.mobile
              mail = user.user_info.mail

              # send ...

   * 如果你需要自定义通知的文案，则需重写
     ``send_password_expiration_msg`` , ``send_login_failure_msg`` , ``send_user_locked_msg``
     ，具体代码参考 ``BaseBackend``

   * 如果你需要缓存全局的token或者其他东西，可以使用 ``BaseBackend`` 自带的三个方法
     ``cache_set`` , ``cache_get`` , ``cache_del`` ，具体代码参考 ``BaseBackend``

2. 把你的类添加到配置中，并重启

   .. code-block:: python
      :caption: config.py

      NOTIFICATION_BACKEND = {
            # 自定义的backend需要使用绝对路径
            'custom.my_backend.MyBackend':{
                  'data':'my data'
            }
      }



----------------------

.. _custom_password_validator:

自定义密码校验器
====================

1. 创建文件 ``custom/my_validator.py`` ，
编写你的类继承 ``BaseBackend`` 并实现 ``__init__`` , ``validate`` , ``get_help_text`` 方法

   .. code-block:: python
      :caption: my_validator.py

      import re
      from django.core.exceptions import ValidationError

      class RegexValidator(object):

          def __init__(self, pattern=None):
              self.pattern = pattern

          def validate(self, password, user=None):
              """
              :param password: 输入的密码
              :param user: User类，需要注意的是user有可能为None（比如创建时）;
                           如果你的规则依赖user当user为None时直接返回。
                           另外user.user_info也有可能为None
              """
              if not re.match(self.pattern, password):
                  raise ValidationError("不能匹配正则 '%s'" % self.pattern)

          def get_help_text(self):
              return "必须匹配正则 '%s'" % self.pattern


2. 把你的类添加到配置中，并重启

   .. code-block:: python
      :caption: config.py

      PASSWORD_VALIDATORS = {
            # 自定义的校验器需要使用绝对路径
            'custom.my_validator.RegexValidator':{
                  'pattern':r'^a'
            }
      }


