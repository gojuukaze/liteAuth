********************
LDAP Server说明
********************

liteAuth并没有完全实现LDAP，精简了大部分LDAP的功能，同时LDAP服务只能查询不能修改，修改需要通过HTTP服务进行。

如果你想快速接入LDAP直接看： :ref:`接入liteAuth配置示例<app>`  。


使用时需要注意下列几点（如果你之前没了解过LDAP，第二条之后可以忽略不看）：

  1. ``uid=ldap`` 这个用户是只读用户，应用接入ldap时bind的用户应使用这个。

  2. liteAuth移除了"dc","cn","ou"等概念，
     取而代之的是使用"uid"作为用户唯一的标识，因此用户的"dn"中只有"uid"。如：``uid=admin`` 。

     也是因此，在liteAuth中只能搜索到用户。

  #. liteAuth会忽略"dn"中非"uid"的部分，
     比如 ``uid=admin,ou=user,dc=abc,dc=com`` liteAuth会识别为 ``uid=admin`` 。

  #. liteAuth精简了search的参数， **搜索用户** 时只有 "filter"与"attributes"两个参数是有用的。

  #. liteAuth把用户的属性分为“属性字段”，“非属性字段”，搜索的条件只能是“属性字段”以及"uid"。

     属性字段有： ``['name', 'mail', 'mobile', 'ssh_key']`` 。

  #. 如果你之前已经接入了ldap不想修改已有的配置，可以通过配置 ``LDAP_FIELD_MAP`` , ``LITE_AUTH_FIELD_MAP`` 来设置字段的别名。
     具体说明见 :ref:`LDAP_FIELD_MAP<ldap_field_map>`


.. toctree::
   :maxdepth: 2
   :caption: 目录

   ldap_wiki
   diffrence
   app