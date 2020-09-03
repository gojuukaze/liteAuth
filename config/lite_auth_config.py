DEBUG = False

"""
http server 配置
"""
HTTP_LISTEN = '0.0.0.0:8300'
# 一定要以 / 结尾
ADMIN_URL = 'admin/'

# 用户信息中禁止用户自主修改的属性字段，管理员组不会被限制
# 非属性字段用户是不能自己修改的，不用添加
READONLY_ATTRIBUTES = ['mail']

# 通知backend，用户发送密码过期，账户锁定等通知给用户。
# 目前支持 Email(只支持smtp)，FeiShu
# 如果使用自定义的backend，key为绝对路径
NOTIFICATION_BACKEND = {
    # 'Email': {
    #     'host': 'smtp.163.com',
    #     'port': '25',
    #     'username': 'xx@163.com',
    #     'password': 'xx'
    # },

    # 'FeiShu': {
    #     'app_id': 't_xx',
    #     'app_secret': 'xx'
    # },
}

"""
ldap server 配置
（虽然下面是ldap的配置，但对应的代码不一定在ldap server中，可能放到了ldap api中）
"""
LDAP_LISTEN = '0.0.0.0:8389'

SEARCH_LIMIT = 1000

# 用于ldap请求的用户名，此用户不能登录管理后台，相当于只读用户
LDAP_USER = 'ldap'

# ----- LDAP_API -------

# ldap server访问http server的路径
LDAP_API_URL = 'http://127.0.0.1:8300'

# LDAP_API请求的超时时间，秒
# 一般不需要修改，
# 如果遇到errorMessage为HttpServerNeverReceived错误，可以尝试调大此项
# (如果出现需要修改此项才能正常返回的情况，请反馈给我)
LDAP_API_TIMEOUT = 3

# LDAP_API登录凭证的有效期，秒 (同时也是ldap连接的超时时间)
# ldap_bind会获取登录凭证以供后续请求验证身份
LDAP_API_AUTH_EXPIRY = 60

# ldap字段对应的liteAuth字段（key必须是全小写，value区分大小写）
# ldap请求时会把filter条件中的key替换为map中的值
LDAP_FIELD_MAP = {
    'cn': 'uid',
    'sn': 'uid',
    'userpassword': 'password',
    'ou': 'groups',
}

# liteAuth字段对应的ldap字段（key区分大小写，value必须是全小写）
# ldap返回用户信息时，会把用户属性的key替换为map中的值
LITE_AUTH_FIELD_MAP = {}

"""
策略配置
"""

# ------ uid校验 ------

# uid匹配的正则（字符串前面的r，可以防止特殊字符被转义）
UID_VALIDATOR = r'^[\w-]+\Z'
# uid规则说明
UID_VALIDATOR_MSG = 'uid只允许字母，数字，下划线（_），横杆（-）'

# ------ 用户锁定策略 ------

# 最大连续登录失败次数，0表示无限制
MAX_LOGIN_ATTEMPT_NUM = 5
# n秒后重置登录失败次数
RESET_LOGIN_ATTEMPT_NUM_AFTER = 60
# 锁定时间，秒
USER_LOCK_DURATION = 60 * 5

# ------ 密码校验 ------

# 密码校验器
# 如果使用自定义的校验器，key为绝对路径，如: 'your_path.your_validator.FooValidator'
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

# ------ 密码其他配置 ------

# 密码有效期，天
MAX_PASSWORD_AGE = 180

"""
LOG配置
"""
LOG_PATH = './log'
# 多大后切割，默认10mb
LOG_MAX_BYTES = 1027 * 1024 * 10
# 保留几分
LOG_BACKUP_COUNT = 10
