import random
from django.conf import settings
from hashids import Hashids
import string

hashids = Hashids(salt=settings.SECRET_KEY, alphabet=string.digits + string.ascii_letters)


def encode_id(id):
    return hashids.encode(id)


def decode_id(hashid):
    return hashids.decode(hashid)[0]
