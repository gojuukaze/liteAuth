from config.lite_auth_config import *
from config.config import *

if not ADMIN_URL.endswith('/'):
    ADMIN_URL += '/'
