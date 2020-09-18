import unittest


class Test1(unittest.TestCase):
    def test_bind(self):
        self.assertEqual('Loo'.upper(), 'LOO')
