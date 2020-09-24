*********************
Docker安装
*********************


1. 创建必要目录，修改配置  
===========================

若在**非生产环境**并且使用nginx镜像可跳过这步

.. code-block:: 

   mkdir liteauth_data
   cd liteauth_data
   touch config.py

在 ``config.py`` 中添加配置

.. code-block:: python

   # 访问lite auth的站点地址，填ip或域名。
   # 部署时需要使用nginx或apache监听此地址，并把请求转发到docker绑定的地址
   LITE_AUTH_URL = 'http://192.168.x.x:8080'

   ADMIN_URL = 'admin/'

   # ldap api的地址，ldap服务会请求这个地址。
   # 其实就是LITE_AUTH_URL，不过建议写内网地址
   LDAP_API_URL = 'http://192.168.x.x:8080'


.. warning::

   docker部署时 ``HTTP_LISTEN`` , ``LDAP_LISTEN`` 不能修改

2. 运行 
===============

.. code-block::
   
   # 8300为http服务地址，8389为ldap服务地址
   docker run -d --name=liteauth \
   --restart=always \
   -p 8300:8300 -p 8389:8389 \
   -v /your_path/liteauth_data:/app/liteauth/docker_data \
   gojuukaze/liteauth:0.1.0


.. note::

   你可以使用 ``-e LITE_AUTH_SECRET_KEY=xxx`` 指定 ``SECRET_KEY`` 
   或者在 ``liteauth_data/config.py`` 中配置

.. note::

   使用``docker run -it gojuukaze/liteauth:0.1.0 ./lite_auth.py gen-secret-key`` 可以生成 ``SECRET_KEY``

.. note::

   对于运行中的容器，使用 ``docker exec -it liteauth python manage.py show_secret_key``
   查看 ``SECRET_KEY``


3. 代理请求 
===============

默认的运行方式并不具备抗DOS攻击的能力，并且代理静态文件的能力一般。
因此需要使用nginx代理请求。下列给出nginx的配置样例 ::

    server {
        # 如果你修改了LITE_AUTH_URL，改为对应的值
        listen       8080;
        server_name  192.168.x.x;
        
        # 替换为你的路径
        root /your_path/liteauth_data;
        
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
            # 如果你修改了docker监听的地址，改为对应的值
            proxy_pass http://127.0.0.1:8300;
        }
    }


4. 开始使用 
===============

访问 http://192.168.x.x:8080 初始化并使用。注意：初始化页面只有第一次使用时能进入
