"""
pip install python-ldap (https://www.python-ldap.org/)

导入csv:
```
uid,name,password（从csv导入时不会校验密码）,重置密码后可用（0:false; 1:true）,"groups（填gid,多个gid用逗号分隔；不存在的组会自动创建）",mobile,mail
u1,name1,1,1,"admin,group1",130,1@a.com
u2,name2,1,0,g1,131,2@a.com
u3,name3,1,0,g1,132,3@a.com
u4,name4,1,0,"g1,g2",133,4@a.com
u5,name5,1,0,"g1,g2",134,5@a.com
u6,name6,1,0,"g1,g2",135,6@a.com
```
"""

import unittest
# 这个import很慢，不知道为啥
import ldap
from ldap.controls import SimplePagedResultsControl


class Test1(unittest.TestCase):
    url = 'ldap://127.0.0.1:8389'

    def setUp(self) -> None:
        super(Test1, self).setUp()
        self.client = ldap.initialize('ldap://127.0.0.1:8389')

    def tearDown(self) -> None:
        super(Test1, self).tearDown()
        self.client.unbind_s()

    def test1(self):
        # 密码错误
        try:
            self.client.simple_bind_s('uid=ldap', '12')
        except ldap.INVALID_CREDENTIALS as e:
            self.assertEqual(e.args[0]['info'], 'invalidCredentials')

        # 密码过期
        try:
            self.client.simple_bind_s('uid=u1', '1')
        except ldap.INVALID_CREDENTIALS as e:
            self.assertIn('passwordExpiration', e.args[0]['info'])
        # 账号锁定
        for i in range(5):
            try:
                self.client.simple_bind_s('uid=u2', '12')
            except:
                pass
        try:
            self.client.simple_bind_s('uid=u2', '1')
        except ldap.INVALID_CREDENTIALS as e:
            self.assertIn('tooManyLoginAttempts', e.args[0]['info'])

        u = self.client.simple_bind_s('uid=ldap', '1')
        self.assertEqual(u[0], 97)
        self._test_search()
        self._test_search_page()

    def _test_search(self):
        users = self.client.search_s("", ldap.SCOPE_SUBTREE)
        self.assertEqual(len(users), 8)

        users = self.client.search_s("", ldap.SCOPE_SUBTREE, 'uid=*')
        self.assertEqual(len(users), 8)

        users = self.client.search_s("", ldap.SCOPE_SUBTREE, 'uid=u*')
        self.assertEqual(len(users), 6)

        # 测试LDAP_FIELD_MAP
        u = self.client.search_s("", ldap.SCOPE_SUBTREE, 'uid=u1')
        u2 = self.client.search_s("", ldap.SCOPE_SUBTREE, 'cn=u1')
        self.assertEqual(u, u2)
        self.assertEqual(u[0][0], 'uid=u1')

        u = self.client.search_s("", ldap.SCOPE_SUBTREE, '(&(uid=u1)(name=name1))')
        self.assertEqual(u[0][0], 'uid=u1')

        users = self.client.search_s("", ldap.SCOPE_SUBTREE, '(|(uid=u1)(name=name2))')
        self.assertEqual(users[0][0], 'uid=u1')
        self.assertEqual(users[1][0], 'uid=u2')

        users = self.client.search_s("", ldap.SCOPE_SUBTREE, '(!(uid=u*))')
        self.assertEqual(len(users), 2)

        users = self.client.search_s("", ldap.SCOPE_SUBTREE, attrlist=['uid', 'mail', 'xx'])
        self.assertEqual(len(users), 8)
        self.assertIn('mail', users[0][1])
        self.assertNotIn('name', users[0][1])

    def _test_search_page(self):
        """
        分页测试
        """
        size = 2
        cookie = ''
        ctl = SimplePagedResultsControl(True, size=size, cookie=cookie)
        users = []
        while True:
            id = self.client.search_ext("", ldap.SCOPE_SUBTREE, "uid=u*", serverctrls=[ctl])
            type, data, id, ctrls = self.client.result3(id)
            users.extend(data)
            if ctrls[0].cookie:
                self.assertEqual(len(data), 2)
                ctl.cookie = ctrls[0].cookie
            else:
                break
        self.assertEqual(len(users), 6)
        self.assertEqual(users[0][0], 'uid=u1')

    def test2(self):
        """
        测试权限
        """
        # 匿名搜索
        try:
            users = self.client.search_s("", ldap.SCOPE_SUBTREE, 'uid=*')
        except ldap.INSUFFICIENT_ACCESS as e:
            self.assertEqual(e.args[0]['desc'], 'Insufficient access')

        self.client.simple_bind_s('uid=u3', '1')
        users = self.client.search_s("", ldap.SCOPE_SUBTREE, 'uid=*')
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0][0], 'uid=u3')

        users = self.client.search_s("", ldap.SCOPE_SUBTREE, 'uid=u1')
        self.assertEqual(len(users), 0)


if __name__ == '__main__':
    unittest.main()
