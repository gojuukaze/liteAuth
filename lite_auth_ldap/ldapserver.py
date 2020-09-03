"""
code base on ldaptor.protocols.ldap.ldapserver
"""
from ldaptor import interfaces
from ldaptor.protocols import pureldap
from ldaptor.protocols.ldap import ldaperrors, distinguishedname
from ldaptor.protocols.ldap.ldapserver import BaseLDAPServer, LDAPServerConnectionLostException
from twisted.internet import defer
from twisted.python import log


class BaseLiteAuthServer(BaseLDAPServer):
    def queue(self, id, op):
        if not self.connected:
            raise LDAPServerConnectionLostException()
        controls = getattr(op, 'controls', None)
        msg = pureldap.LDAPMessage(op, id=id, controls=controls)
        if self.debug:
            log.msg('S->C %s' % repr(msg), debug=True)
        self.transport.write(msg.toWire())

    def checkControls(self, controls):
        ctls = []
        if controls is not None:
            for control_type, criticality, control_value in controls:
                # 把control_value转为str，否则http请求时会报错
                ctls.append((control_type, criticality,
                             str(control_value, encoding='utf-8') if control_value else control_value))
        return ctls


class LiteAuthLDAPServer(BaseLiteAuthServer):
    cookies = None

    fail_LDAPBindRequest = pureldap.LDAPBindResponse

    def _bind_callback(self, data):
        cookies, user = data

        self.cookies = cookies
        return pureldap.LDAPBindResponse(
            resultCode=ldaperrors.Success.resultCode,
            matchedDN=user.dn)

    def handle_LDAPBindRequest(self, request, controls, reply):
        if request.version != 3:
            raise ldaperrors.LDAPProtocolError(
                'Version %u not supported' % request.version)

        # self.checkControls(controls)

        if request.dn == b'':
            # anonymous bind
            return pureldap.LDAPBindResponse(resultCode=0)
        else:
            dn = str(request.dn, encoding='utf8')
            password = str(request.auth, encoding='utf8')

            # handler = interfaces.IConnectedLDAPEntry(self.factory)
            handler = self.factory.handler
            d = handler.bind(dn, password)

            d.addCallback(self._bind_callback)

            return d

    def handle_LDAPUnbindRequest(self, request, controls, reply):
        self.cookies = None
        self.transport.loseConnection()

    def _search(self, handler, request, controls, reply):
        def _send_user(user):
            reply(pureldap.LDAPSearchResultEntry(
                objectName=user.dn,
                attributes=user.items(),
            ))

        d = handler.search(self.cookies, filter_obj=request.filter, attributes=request.attributes,
                           controls=controls, callback=_send_user)

        def _done(ctls):
            r = pureldap.LDAPSearchResultDone(
                resultCode=ldaperrors.Success.resultCode)
            if ctls:
                r.controls = ctls
            return r

        d.addCallback(_done)
        return d

    def _cbSearchLDAPError(self, reason):
        reason.trap(ldaperrors.LDAPException)
        return pureldap.LDAPSearchResultDone(
            resultCode=reason.value.resultCode,
            errorMessage=reason.getErrorMessage())

    def _cbSearchOtherError(self, reason):
        return pureldap.LDAPSearchResultDone(
            resultCode=ldaperrors.other,
            errorMessage=reason.getErrorMessage())

    fail_LDAPSearchRequest = pureldap.LDAPSearchResultDone

    def getRootDSE(self, request, reply):
        reply(pureldap.LDAPSearchResultEntry(
            objectName='',
            attributes=[('supportedLDAPVersion', ['3']),
                        ('namingContexts', ['dc=liteauth']),
                        ('supportedExtension', [b'1.2.840.113556.1.4.319'])]
        ))
        return pureldap.LDAPSearchResultDone(
            resultCode=ldaperrors.Success.resultCode)

    def handle_LDAPSearchRequest(self, request, controls, reply):
        ctls = self.checkControls(controls)
        if self.cookies is None:
            raise ldaperrors.LDAPInsufficientAccessRights()

        if (request.baseObject == b''
                and request.scope == pureldap.LDAP_SCOPE_baseObject
                and request.filter == pureldap.LDAPFilter_present('objectClass')):
            return self.getRootDSE(request, reply)

        handler = self.factory.handler
        d = self._search(handler, request, ctls, reply)
        d.addErrback(self._cbSearchLDAPError)
        d.addErrback(defer.logError)
        d.addErrback(self._cbSearchOtherError)
        return d
