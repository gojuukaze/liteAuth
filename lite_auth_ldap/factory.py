import sys

from lite_auth_ldap.handler import LiteAuthHandler
from lite_auth_ldap.ldapserver import LiteAuthLDAPServer
from twisted.internet.protocol import ServerFactory


class LiteAuthLDAPFactory(ServerFactory):
    protocol = LiteAuthLDAPServer

    def __init__(self, handler):
        self.handler = handler

    def buildProtocol(self, addr):
        proto = self.protocol()
        proto.debug = self.debug
        proto.factory = self
        return proto

