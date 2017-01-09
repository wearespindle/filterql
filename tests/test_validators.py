from pytest import raises

from filterql.exceptions import InvalidValueException
from filterql.lookup_types import (
    DAY, HOUR, ISNULL, MINUTE, MONTH, SECOND, WEEK,
)
from filterql.validators import VALIDATORS


def test_isnull_validator():
    """
    Test the isnull_validator.
    """
    validator = VALIDATORS[ISNULL]
    message = 'Only True or False allowed for ISNULL lookup type.'

    validator(True)
    validator(False)

    with raises(InvalidValueException) as excinfo:
        validator('null')

    assert str(excinfo.value) == message


def test_month_validator():
    validator = VALIDATORS[MONTH]
    message = 'Month needs to be 1 <= month <= 12'

    for number in range(1, 13):
        validator(number)

    with raises(InvalidValueException) as excinfo:
        validator(0)

    assert str(excinfo.value) == message

    with raises(InvalidValueException) as excinfo:
        validator(13)

    assert str(excinfo.value) == message

    message = 'Value needs to be an integer'
    with raises(InvalidValueException) as excinfo:
        validator('spindle')

    assert str(excinfo.value) == message


def test_week_validator():
    validator = VALIDATORS[WEEK]
    message = 'Week needs to be 1 <= week <= 54'

    for number in range(1, 55):
        validator(number)

    with raises(InvalidValueException) as excinfo:
        validator(0)

    assert str(excinfo.value) == message

    with raises(InvalidValueException) as excinfo:
        validator(55)

    assert str(excinfo.value) == message

    message = 'Value needs to be an integer'
    with raises(InvalidValueException) as excinfo:
        validator('spindle')

    assert str(excinfo.value) == message


def test_day_validator():
    validator = VALIDATORS[DAY]
    message = 'Day needs to be 1 <= day <= 31'

    for number in range(1, 32):
        validator(number)

    with raises(InvalidValueException) as excinfo:
        validator(0)

    assert str(excinfo.value) == message

    with raises(InvalidValueException) as excinfo:
        validator(32)

    assert str(excinfo.value) == message

    message = 'Value needs to be an integer'
    with raises(InvalidValueException) as excinfo:
        validator('spindle')

    assert str(excinfo.value) == message


def test_hour_validator():
    validator = VALIDATORS[HOUR]
    message = 'Hour needs to be 0 <= hour <= 23'

    for number in range(24):
        validator(number)

    with raises(InvalidValueException) as excinfo:
        validator(-1)

    assert str(excinfo.value) == message

    with raises(InvalidValueException) as excinfo:
        validator(25)

    assert str(excinfo.value) == message

    message = 'Value needs to be an integer'
    with raises(InvalidValueException) as excinfo:
        validator('spindle')

    assert str(excinfo.value) == message


def test_minute_validator():
    validator = VALIDATORS[MINUTE]
    message = 'Minute needs to be 0 <= minute <= 59'

    for number in range(60):
        validator(number)

    with raises(InvalidValueException) as excinfo:
        validator(-1)

    assert str(excinfo.value) == message

    with raises(InvalidValueException) as excinfo:
        validator(60)

    assert str(excinfo.value) == message

    message = 'Value needs to be an integer'
    with raises(InvalidValueException) as excinfo:
        validator('spindle')

    assert str(excinfo.value) == message


def test_second_validator():
    validator = VALIDATORS[SECOND]
    message = 'Second needs to be 0 <= second <= 60'

    for number in range(61):
        validator(number)

    with raises(InvalidValueException) as excinfo:
        validator(-1)

    assert str(excinfo.value) == message

    with raises(InvalidValueException) as excinfo:
        validator(61)

    assert str(excinfo.value) == message

    message = 'Value needs to be an integer'
    with raises(InvalidValueException) as excinfo:
        validator('spindle')

    assert str(excinfo.value) == message
