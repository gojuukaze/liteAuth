import re

from django.conf import settings
from django.core import validators
from django.utils.deconstruct import deconstructible


@deconstructible
class UidValidator(validators.RegexValidator):
    regex = settings.UID_VALIDATOR
    message = settings.UID_VALIDATOR_MSG

