import datetime
import decimal
import json
import uuid

from django.utils.duration import duration_iso_string
from django.utils.functional import Promise
from django.utils.timezone import is_aware

from utils.datetime_helper import datetime_to_str


class LiteAuthJsonEncoder(json.JSONEncoder):
    """
    JSONEncoder subclass that knows how to encode date/time, decimal types, and
    UUIDs.
    """

    def default(self, o):
        # See "Date Time String Format" in the ECMA-262 specification.
        if isinstance(o, datetime.datetime):
            return datetime_to_str(o)

        elif isinstance(o, datetime.date):
            return o.isoformat()
        elif isinstance(o, datetime.time):
            if is_aware(o):
                raise ValueError("JSON can't represent timezone-aware times.")
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return r
        elif isinstance(o, datetime.timedelta):
            return duration_iso_string(o)
        elif isinstance(o, (decimal.Decimal, uuid.UUID, Promise)):
            return str(o)
        elif isinstance(o, bytes):
            return str(o, encoding='utf-8')
        else:
            return super().default(o)
