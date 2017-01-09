from .lookup_types import LOOKUP_TYPES


class DecodeException(Exception):
    pass


class InvalidFormat(Exception):
    pass


class InvalidValueException(Exception):
    pass


class UnsupportedLookupException(Exception):

    def __init__(self, lookup):
        message = '`%s` is not a supported lookup! Supported lookups are: %s' % (lookup, LOOKUP_TYPES)

        super(type(self), self).__init__(message)
