************
升级
************



普通安装升级
===================

.. code-block::

   ./lite_auth.py stop
   git pull
   ./lite_auth.py init
   ./lite_auth.py start

docker安装升级
===================

.. warning::

   如果之前且启动时没有配置过 ``SECRET_KEY`` 。升级前先备份 ``SECRET_KEY`` ，再次启动时指定 ``SECRET_KEY`` 。

   备份SECRET_KEY见： :ref:`备份SECRET_KEY<backup_secret_key>`

   指定SECRET_KEY见： :ref:`指定SECRET_KEY<docker_set_secret_key>`

.. code-block::

   docker pull gojuukaze/liteauth:x.x.x
   docker stop liteauth
   docker rm liteauth
   # 启动liteauth，启动命令见安装部分

