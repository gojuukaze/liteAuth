*********************
普通安装
*********************

1. 环境准备
==============

安装LiteAuth需要下列环境：

* Linux/Mac OS
* Python3.6+ ( maybe 3.4, 3.5 )
* git
* nginx或其他同类软件

安装前建议你创建个虚拟环境（虽然这部不必须的，但强烈建议你这么做）::
   
   python3 -m venv /your_path/liteAuth_env
   source /your_path/liteAuth_env


2. 拉取代码
==============

.. code-block::

   git clone https://github.com/gojuukaze/liteAuth.git

3. 初始化
================

.. code-block:: 

   cd liteAuth

   # 你可以添加参数 "-i https://mirrors.aliyun.com/pypi/simple/" 加速下载
   pip3 install -r requirements.txt

   ./lite_auth.py init

.. note::

   初始化时会在在 ``config/config.py`` 中生成一个随机的密钥 ``SECRET_KEY`` ，这个请保存这个密钥不要丢失。
   迁移服务时必须使用相同的密钥。 

   * 初始化时可以使用 ``-s`` 设置秘钥。运行 ``./lite_auth.py init --help`` 查看说明。
   * 你可以使用 ``./lite_auth.py gen-secret-key`` 生成随机的密钥

.. note::
   
   如果你没使用虚拟环境，在执行 ``./lite_auth.py`` 时可能会报错。
   若报错尝试用 ``python3 lite_auth.py`` 代替

4. 修改配置文件
=================

下面给出几个关键配置，全部配置参考 :ref:`配置说明<config>` 。 

.. code-block:: python

   HTTP_LISTEN = '0.0.0.0:8300'

   # 访问lite auth的站点地址，填ip或域名。
   # 部署时需要使用nginx或apache监听此地址，并把请求转发到 HTTP_LISTEN
   LITE_AUTH_URL = 'http://192.168.x.x:8080'

   ADMIN_URL = 'admin/'

   LDAP_LISTEN = '0.0.0.0:8389'
   # ldap api的地址，ldap服务会请求这个地址。
   # 其实就是LITE_AUTH_URL，不过建议写内网地址
   LDAP_API_URL = 'http://127.0.0.1:8080'

   # 通知backend，用于发通知给用户（具体说明参考 “配置”-“通知相关” ）
   NOTIFICATION_BACKEND={}

.. note::

   ``NOTIFICATION_BACKEND`` 不是必须的，但强烈建议你配置一个backend。
   很多有的接入LDAP的服务并不会返回LDAP的错误信息，导致用户登录时不知道是什么原因造成登录失败。


5. 运行
============

使用下面命令运行

.. code-block::

   ./lite_auth.py start
   # 你可以使用 ./lite_auth.py start --help 查看帮助

.. note::

   如果只是为了快速体验，可以在配置中添加 `DEBUG=True` 
   并把 ``LITE_AUTH_URL`` ， ``LDAP_API_URL`` 修改为 ``HTTP_LISTEN`` 的地址，运行后直接访问。


.. _nginx_config:

6. 代理请求
================

默认的运行方式并不具备抗DOS攻击的能力，并且代理静态文件的能力一般。
因此需要使用nginx代理请求。下列给出nginx的配置样例 ::

    server {
        # 如果你修改了LITE_AUTH_URL，改为对应的值
        listen       8080;
        server_name  127.0.0.1 192.168.x.x;

        # 替换为你的路径
        root /your_path/liteAuth;
        
        location / {
            try_files $uri @proxy_to_app;
        }
    
        location @proxy_to_app {
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header Host $http_host;
            # we don't want nginx trying to do something clever with
            # redirects, we set the Host: header above already.
            proxy_redirect off;
            # 如果你修改了HTTP_LISTEN，改为对应的值
            proxy_pass http://127.0.0.1:8300;
        }
    }


7. 开始使用
==============

访问 http://192.168.x.x:8080 初始化并使用。注意：初始化页面只有第一次使用时能进入

接入ldap参考： :ref:`接入liteAuth配置示例<app>`
