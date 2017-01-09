from datetime import date, datetime
import traceback

from dateutil import parser
import simplejson as json

from .exceptions import DecodeException


class TypeEncoder(json.JSONEncoder):
    """
    Custome encoder for unsupported types.
    """
    def default(self, obj):
        """
        Encode specific types.

        Only executed on unknown JSON types.

        Args:
            obj: The obj of a unknown JSON type.
        """
        encode = ENCODERS.get(type(obj))

        if encode:
            return encode(obj)
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)


def type_decoder(dct):
    """
    Decodes a value if there is a type given for the value.

    Args:
        dct: The dict to decode.

    Returns:
        dict: The dict with certain types decoded.

    Raises:
        DecodeException: When decoding of the type failed.
    """
    # Avoid circular import.
    from .lookup import TYPE_KEY, VALUE_KEY

    value_type = dct.get(TYPE_KEY)
    if value_type:
        decode = DECODERS.get(value_type)
        if decode:
            try:
                dct[VALUE_KEY] = decode(dct[VALUE_KEY])
            except:
                trace = traceback.format_exc()
                raise DecodeException(
                    'Error decoding type `%s` %s\n%s' % (value_type, dct[VALUE_KEY], trace))
    return dct


def decode_date(date_string):
    """
    Decode a date string into a python date.

    Args:
        date_string (string): The string containing the date.

    Returns:
        date: The decoded date.
    """
    return datetime.strptime(date_string, '%Y-%m-%d').date()


def decode_datetime(datetime_string):
    """
    Decode a datetime string into a python datetime.

    Args:
        datetime_string (string): The string containing the datetime.

    Returns:
        datetime: The decoded datetime.
    """
    return parser.parse(datetime_string, fuzzy=False)


DECODERS = {
    date.__name__: decode_date,
    datetime.__name__: decode_datetime,
}

ENCODERS = {
    date: lambda x: x.isoformat(),
    datetime: lambda x: x.isoformat(),
}
