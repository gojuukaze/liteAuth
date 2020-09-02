from ldaptor.protocols import pureber
from ldaptor.protocols.ldap import ldaperrors

"""
rfc: https://www.ietf.org/rfc/rfc2696.txt
"""


class PagedResultsControl(object):
    control_type = '1.2.840.113556.1.4.319'

    @classmethod
    def fromBER(cls, criticality, control_value):
        ber_context = pureber.BERDecoderContext()
        obj, _ = pureber.berDecodeObject(ber_context, control_value)
        size = obj[0].value
        cookie = obj[1].value

        if size <= 0:
            raise ldaperrors.LDAPUnavailableCriticalExtension('Page size must be greater than 0')

        if cookie:
            obj, _ = pureber.berDecodeObject(ber_context, cookie)
            remain_count = obj[0].value
            last_id = obj[1].value
        else:
            remain_count = None
            last_id = 0
        return cls(criticality, size, remain_count, last_id)

    def __init__(self, criticality=False, size=0, remain_count=0, last_id=0):
        self.criticality = criticality
        self.size = size
        self.remain_count = remain_count
        self.last_id = last_id

    @property
    def ctl(self):
        return self.control_type, self.criticality, self.encode_control_value()

    @property
    def cookie(self):
        if self.remain_count <= 0:
            return b''
        return pureber.BERSequence([
            pureber.BERInteger(self.remain_count),
            pureber.BERInteger(self.last_id),
        ]).toWire()

    def encode_control_value(self):
        return pureber.BERSequence([
            pureber.BERInteger(self.size),
            pureber.BEROctetString(self.cookie),
        ]).toWire()

    def __repr__(self):
        return '{} {} {} {}'.format(self.criticality, self.size, self.remain_count, self.last_id)
