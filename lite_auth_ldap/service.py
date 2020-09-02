from twisted.internet import reactor
from twisted.application import service

from lite_auth_ldap.factory import LiteAuthLDAPFactory
from lite_auth_ldap.handler import LiteAuthHandler


class LiteAutLDAPService(service.Service):
    def __init__(self, portNum, ip, debug):
        self.portNum = portNum
        self.interface = ip
        self.debug = debug

    def startService(self):
        factory = LiteAuthLDAPFactory(LiteAuthHandler())
        factory.debug = self.debug
        self._port = reactor.listenTCP(self.portNum, factory, interface=self.interface)

    def stopService(self):
        return self._port.stopListening()
