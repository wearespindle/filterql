from datetime import date, datetime

from pytest import raises

from filterql.exceptions import DecodeException
from filterql.lookup import TYPE_KEY, VALUE_KEY
from filterql.utils import (
    decode_date,
    decode_datetime,
    ENCODERS,
    TypeEncoder,
    type_decoder,
)


def test_type_encoder():
    """
    Test JSON encoding of Decimal, date and datetime.
    """
    date_obj = date(2017, 6, 6)
    the_input = {'date': date_obj}
    expected = '{"date": "%s"}' % date_obj.isoformat()

    result = TypeEncoder().encode(the_input)
    assert result == expected

    datetime_obj = datetime(2017, 6, 6, 13, 37, 0)
    the_input = {'datetime': datetime_obj}
    expected = '{"datetime": "%s"}' % datetime_obj.isoformat()

    result = TypeEncoder().encode(the_input)
    assert result == expected

    class Unknown():
        pass
    unknown_obj = Unknown()

    with raises(TypeError):
        TypeEncoder().encode(unknown_obj)


def test_type_decoder():
    """
    Test type decoding of date, datetime and Decimal.
    """
    _date = date(2017, 6, 6)
    date_dict = {VALUE_KEY: ENCODERS.get(type(_date))(_date), TYPE_KEY: date.__name__}
    decoded = type_decoder(date_dict)

    assert decoded.get(VALUE_KEY) == _date

    _datetime = datetime(2017, 6, 6, 13, 37, 0)
    datetime_dict = {VALUE_KEY: ENCODERS.get(type(_datetime))(_datetime), TYPE_KEY: datetime.__name__}
    decoded = type_decoder(datetime_dict)

    assert decoded.get(VALUE_KEY) == _datetime

    # Test decoding datetime with given type `date`.
    _datetime = datetime(2017, 6, 6)
    decimal_dict = {VALUE_KEY: ENCODERS.get(type(_datetime))(_datetime), TYPE_KEY: date.__name__}

    with raises(DecodeException):
        decoded = type_decoder(decimal_dict)


def test_decode_date():
    """
    Test decoding of date string.
    """
    date_obj = date(2017, 6, 6)

    result = decode_date(date_obj.isoformat())

    assert result == date_obj


def test_decode_datetime():
    """
    Test decoding of datetime string.
    """
    datetime_obj = datetime(2017, 6, 6, 13, 37, 0)

    result = decode_datetime(datetime_obj.isoformat())

    assert result == datetime_obj
