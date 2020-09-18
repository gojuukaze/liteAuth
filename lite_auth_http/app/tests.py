from django.test import TestCase, modify_settings, SimpleTestCase

# Create your tests here.
import unittest
from django.test import Client

from lite_auth_http.app.db_manager.user_info import get_user_info_by_uid
from lite_auth_http.app.forms import AddAdminForm


class InitTest(TestCase):
    password = 'asd123--?sdf3333'

    def setUp(self):
        self.client = Client()

    def test_password_valida(self):
        f = AddAdminForm({'uid': 'admin', 'name': 'hhh', 'password': self.password})
        self.assertTrue(f.is_valid(), True)
        # 测试密码校验
        # 长度
        f = AddAdminForm({'uid': 'admin', 'name': 'hhh', 'password': 'ewqa2sd'})
        f.is_valid()
        self.assertTrue('password' in f.errors)
        self.assertTrue('太短' in f.errors['password'][0])

        # 复杂的
        f = AddAdminForm({'uid': 'admin', 'name': 'hhh', 'password': 'qweasdgfdrtyewe'})
        f.is_valid()
        self.assertTrue('password' in f.errors)
        self.assertTrue('包含2种字符' in f.errors['password'][0])

        # 相似度
        f = AddAdminForm({'uid': 'admin', 'name': 'hhh', 'password': 'admin'})
        f.is_valid()
        self.assertTrue('password' in f.errors)
        self.assertTrue('相似' in ''.join(f.errors['password']))

    def test_init(self):
        # Issue a GET request.
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/',
                                    {'创建一个管理员账户-uid': 'admin',
                                     '创建一个管理员账户-name': 'admin',
                                     '创建一个管理员账户-password': self.password,
                                     '创建一个管理员账户-groups': 'foo,xx',
                                     '创建一个管理员账户-mobile': '111',

                                     '创建一个LDAP账户-uid': 'xxx',
                                     '创建一个LDAP账户-password': self.password,
                                     '创建一个LDAP账户-name': 'nnnmmm',
                                     '创建一个LDAP账户-groups': 'g1,g2',
                                     }
                                    )
        self.assertEqual(response.status_code, 302)

        # 初始化完成后就不访问了
        response = self.client.get('/')
        self.assertEqual(response.status_code, 404)

        # 检查数据库字段
        u = get_user_info_by_uid('admin')
        self.assertEqual(u.mobile, '')
        gs = list(u.groups.all().values_list('gid', flat=True))
        self.assertEqual(gs, ['admin'])

        u = get_user_info_by_uid('ldap')
        self.assertEqual(u.mobile, '')
        self.assertEqual(u.name, 'ldap')
        gs = list(u.groups.all().values_list('gid', flat=True))
        self.assertEqual(gs, [])

        self._test_admin_login()

    # def _test_admin_login(self):
    # 
    #     response = self.client.get('/admin/')
    #     print(response.cookies)
    # 
    #     self.assertRedirects(response, '/admin/login/?next=/admin/')
    #     response = self.client.post('/admin/login/?next=/admin/', {'username': 'ldap', 'password': self.password,'next':'/admin/'})
    #     print(response)
    #     print(response.__dict__)
    # 
    #     with open('a.html','wb')as f:
    #         f.write(response.content)
    #     self.assertTrue('没有这个页面的访问权限' in str(response.content, encoding='utf-8'))
    # 
    # 
    # 
    #     response = self.client.post('/admin/login/', {'username': 'admin', 'password': self.password,'next':'/admin/'})
    #     print(response)
