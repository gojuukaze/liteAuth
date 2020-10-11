.. _backup_and_restore:

************
备份和恢复
************

备份liteauth你只需要备份数据库， 以及配置文件（ ``config.py`` ）



普通安装备份数据库
====================
开始之前先别忘了激活虚拟环境

备份
---------

.. code-block::

   cd liteAuth
   python manage.py dumpdata > mybk.json

恢复
--------

如果是重新安装，恢复前先执行初始化 ``./lite_auth.py init``

.. code-block::

   # 如果使用sqlite3数据库，先执行：rm db.sqlite3

   python manage.py loaddata mybk.json

-----------------------------

docker安装备份数据库
====================

备份
-------

.. code-block::

   docker exec -it liteauth python manage.py dumpdata > /app/liteauth/docker_data/mybk.json

复制 ``/your_path/liteauth_data`` 下的 ``mybk.json``

.. _backup_secret_key:

.. admonition:: 备份SECRET_KEY

   如果你是从docker安装，且启动时没有配置过 ``SECRET_KEY`` 。备份时运行下面命令查看 ``SECRET_KEY`` 并保存，
   再次启动时需要指定用这个SECRET_KEY。

   .. code-block::

      docker exec -it liteauth python manage.py show_secret_key

恢复
-------
恢复前要把容器运行起来

.. code-block::

   cp /your_path/mybk.json /your_path/liteauth_data/

   docker exec -it liteauth python manage.py loaddata /app/liteauth/docker_data/mybk.json

