import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from twisted.logger import textFileLogObserver, ILogObserver
from twisted.application import service
from twisted.python.logfile import LogFile

import config

from lite_auth_ldap.service import LiteAutLDAPService

f = LogFile('ldap.log', config.LOG_PATH, rotateLength=config.LOG_MAX_BYTES, maxRotatedFiles=config.LOG_BACKUP_COUNT)

application = service.Application("LiteAuth LDAP Application")
application.setComponent(ILogObserver, textFileLogObserver(f))

ip, port = config.LDAP_LISTEN.split(':')
service = LiteAutLDAPService(int(port), ip)
service.setServiceParent(application)
