.. _config:

************
配置
************

http服务配置
==============

.. py:data:: HTTP_LISTEN

   :default: ``'0.0.0.0:8300'``

.. py:data:: LITE_AUTH_URL

   :default: ``'http://127.0.0.1:8080'``

   访问lite auth的站点地址，填ip或域名。部署时需要使用nginx或apache监听此地址，并把请求转发到 HTTP_LISTEN


.. py:data:: ADMIN_URL

   :default: ``'admin/'``

   管理后台的地址

----------------------

ldap服务配置
==============

.. py:data:: LDAP_LISTEN

   :default: ``'0.0.0.0:8389'``

.. py:data:: SEARCH_LIMIT

   :default: ``1000``

   ldap的search limit

.. py:data:: LDAP_USER

   :default: ``'ldap'``

   用于ldap请求的用户，此用户不能登录管理后台，相当于只读用户。如果在初始化后修改了此项，你需要进数据库手动修改uid

LDAP_API相关
------------------
ldap服务不是直接访问数据库，而是通过ldap api访问。

    .. py:data:: LDAP_API_URL

       :default: ``'http://127.0.0.1:8080'``

       http服务的地址，ldap服务会请求这个地址。其实就是LITE_AUTH_URL，不过建议写内网地址

    .. py:data:: LDAP_API_TIMEOUT

       :default: ``3``

       LDAP_API http请求的超时时间，秒。

       一般不需要修改，如果遇到errorMessage为HttpServerNeverReceived错误，可以尝试调大此项

       .. note::

          如果出现需要修改此项才能正常返回的情况，请反馈给我

    .. py:data:: LDAP_API_AUTH_EXPIRY

       :default: ``60``

       LDAP_API登录凭证的有效期，秒 (同时也是ldap连接的超时时间)。ldap_bind会获取登录凭证以供后续请求验证身份

.. py:data:: LDAP_FIELD_MAP

   :default:

     .. code-block:: python

         LDAP_FIELD_MAP = {
            'cn': 'uid',
            'sn': 'uid',
            'userpassword': 'password',
            'ou': 'groups',
         }

   ldap字段对应的liteAuth字段（key必须是全小写，value区分大小写）。
   ldap请求时会把filter条件中的key替换为map中的值。

   用于已经配置了ldap的服务，不想改配置的参数，则修改此项。

.. py:data:: LITE_AUTH_FIELD_MAP

   :default: ``{}``

   liteAuth字段对应的ldap字段（key区分大小写，value必须是全小写）。
   ldap返回用户信息时，会把用户属性的key替换为map中的值。

   用于已经配置了ldap的服务，不想改配置的参数，则修改此项。

----------------------

策略配置
===============

登录锁定策略
---------------

   .. py:data:: MAX_LOGIN_ATTEMPT_NUM

      :default: ``5``

      最大连续登录失败次数，0表示无限制

   .. py:data:: RESET_LOGIN_ATTEMPT_NUM_AFTER

      :default: ``60``

      n秒后重置登录失败次数

   .. py:data:: USER_LOCK_DURATION

      :default: ``60 * 5``

      锁定时间，秒

密码校验器
--------------------

.. py:data:: PASSWORD_VALIDATORS

   :default:

      .. code-block:: python

         PASSWORD_VALIDATORS = {
              # 长度校验，min_length: 1-30
              'LengthValidator': {'min_length': 8},

              # 密码重用校验，禁止使用前num次使用的密码，0-5
              'ReuseValidator': {'num': 2},

              # 常见密码校验，禁止过于简单的密码，如：1234
              'CommonValidator': {},

              # 属性相似度校验，禁止和uid，mail相似的密码
              'UserInfoSimilarityValidator': {},

              # 复杂度校验
              'CharacterValidator': {
                  'character_types': 2,  # 包含的多少种不同字符, 1-4
                  'symbols': r'''!"#$%&'()*+,-./:<=>?@[\]^_`{|}~'''  # 允许的标点。 注意：格式是 r'''标点'''
              },
         }

   密码校验器，设置密码时的校验。

   自定义的校验器，key为绝对路径，如: 'custom.your_validator.FooValidator'


.. py:data:: MAX_PASSWORD_AGE

   :default: ``180``

   密码有效期，天

---------------------

.. _notification:




通知相关
=============

.. py:data:: NOTIFICATION_BACKEND

   :default: ``{}``

   通知backend，用于发送密码过期，账户锁定等通知给用户。

   如果使用自定义的backend，key为绝对路径，如： ``custom.your_backend.Foo``

   .. note::

      你可以配置多个backend，不过不建议这么做。
      发通知并不是异步的，多个backend或影响请求返回时间。

   自带的bacnkend有：

   * **Email**

     只支持smtp

     .. code-block:: python

         NOTIFICATION_BACKEND={
             'Email': {
                'host': 'smtp.163.com',
                'port': '25',
                'username': 'xx@163.com',
                'password': 'xx'
             }
         }

   * **FeiShu**

     飞书机器人通知

     .. code-block:: python

         NOTIFICATION_BACKEND={
             'FeiShu': {
                 'app_id': 'cli_xx',
                 'app_secret': 'xx'
            },
         }
     
     你需要开通飞书机器人，步骤如下：

       1. 注册 `飞书开发平台 <https://open.feishu.cn/>`_ 。
       2. 并创建企业自建应用，标题图标随意
       #. 获取 ``app_id`` , ``app_secret``
       #. 在"应用功能"中启动机器人功能
       #. 在"权限管理"给予权限： ``用户 - 通过手机号或者邮箱获取用户ID`` , ``消息 - 给多个用户批量发消息`` , ``消息 - 以应用的身份发消息``
       #. 版本管理与发布中创建版本并发布。（需要联系管理员审核通过）

   * **SMS**

     短信通知

     .. code-block:: python

         NOTIFICATION_BACKEND={
             'SMS': {
                 'url': 'http://xxx', # 你的接口地址
                 'method':'post', # 只支持 post, get
                 'json': True, # 提交json格式的数据
             },
         }

     由于不同短信服务商对接方式不一样，无法给个通用的短信backend，需要短信通知你可以自行开发个backend。

     对于不熟悉python的公司，可以使用提供的SMS backend，你需要开发个新接口用于接收backend提交的发送短信的请求。

     这个接口的提交的参数为：mobile, msg



.. py:data:: PASSWORD_EXPIRATION_NOTIFICATION

   :default:

     .. code-block:: python

         PASSWORD_EXPIRATION_NOTIFICATION = {
             # 运行时间
             'crontab': '0 8 * * *',
             # 还剩几天时发通知，不用写0
             'days': [30, 10, 7, 3, 2, 1]
         }

   密码过期通知任务

-----------------

日志相关
==============

.. py:data:: LOG_PATH

   :default: ``'./log'``

.. py:data:: LOG_MAX_BYTES

   :default: ``1024 * 1024 * 10``

   多大后切割，默认10mb

.. py:data:: LOG_BACKUP_COUNT

   :default: ``10``

   保留几份

数据库配置
=================

liteAuth默认使用sqlite3数据库，大多数情况下完全够用了。
如果需要你也可以切换为 ``mysql`` , ``postgresql`` 等数据库。

mysql
--------------
下面给出mysql的配置说明

1. 安装 `mysqlclient <https://pypi.org/project/mysqlclient/>`_ 库。（docker部署不需要）

   .. code-block::

     pip install mysqlclient

2. 在配置文件中添加

   .. code-block:: python

      DATABASES = {
        'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'liteauth_db', # 数据库名
           'USER': 'root', # 账号
           'PASSWORD': 'secret',
           'HOST': '127.0.0.1',
           'POST': 3306,
           'OPTIONS': {
              'charset': 'utf8mb4', # 使用mysql必须设置此项
           },
        }
      }

3. 创建数据库

   .. code-block::

     CREATE DATABASE liteauth_db /*!40100 DEFAULT CHARACTER SET utf8mb4 */;

4. 执行初始化（docker直接重启）

   .. code-block::

     ./lite_auth.py init

postgresql
--------------

1. 安装 `psycopg2 <https://www.psycopg.org/>`_ 库。（docker部署不需要）

   .. code-block::

     pip install psycopg2

2. 在配置文件中添加

   .. code-block:: python

      DATABASES = {
        'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'liteauth_db', # 数据库名
           'USER': 'root', # 账号
           'PASSWORD': 'secret',
           'HOST': '127.0.0.1',
           'POST': 5432,
        }
      }

3. 创建数据库

   .. code-block::

     CREATE DATABASE liteauth_db;


4. 执行初始化（docker直接重启）
   .. code-block::

      ./lite_auth.py init

.. note::

   所以支持的数据库，以及更多说明参考： https://docs.djangoproject.com/en/3.1/ref/databases/


django配置
==============

liteAuth使用django框架，因此同时也继承了django的配置，不过一般不建议你修改这些配置。

django的配置见：https://docs.djangoproject.com/en/3.1/ref/settings/