class User(object):

    def __init__(self, attrs: dict):
        # attrs格式为： { 'dn':'uid=x', 'key': ['value',] }
        # dn的值为字符串, 属性的值为list
        self.attrs = attrs

    def get(self, key, default=None):
        return self.attrs.get(key, default)

    @property
    def dn(self):
        # attrs一定存在dn
        return self.attrs['dn']

    def items(self):
        return [(k, v) for k, v in self.attrs.items() if k != 'dn']
