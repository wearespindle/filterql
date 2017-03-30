from .lookup_types import DAY, HOUR, ISNULL, MINUTE, MONTH, SECOND, WEEK
from .exceptions import InvalidValueException


def integer_validator(value):
    if not isinstance(value, int):
        raise InvalidValueException('Value needs to be an integer')


def day_validator(day):
    integer_validator(day)

    if not (1 <= day <= 31):
        raise InvalidValueException('Day needs to be 1 <= day <= 31')


def month_validator(month):
    integer_validator(month)

    if not (1 <= month <= 12):
        raise InvalidValueException('Month needs to be 1 <= month <= 12')


def week_validator(week):
    integer_validator(week)

    if not (1 <= week <= 54):  # 54 happens every 28 years, next occurence 2028
        raise InvalidValueException('Week needs to be 1 <= week <= 54')


def hour_validator(hour):
    integer_validator(hour)

    if not (0 <= hour <= 23):
        raise InvalidValueException('Hour needs to be 0 <= hour <= 23')


def minute_validator(minute):
    integer_validator(minute)

    if not (0 <= minute <= 59):
        raise InvalidValueException('Minute needs to be 0 <= minute <= 59')


def second_validator(second):
    integer_validator(second)

    if not (0 <= second <= 60):  # 60 to account for leap seconds
        raise InvalidValueException('Second needs to be 0 <= second <= 60')


def isnull_validator(value):
    if not isinstance(value, bool):
        raise InvalidValueException(
            'Only True or False allowed for ISNULL lookup type.')


VALIDATORS = {
    # Date/time related validators.
    MONTH: month_validator,
    WEEK: week_validator,
    DAY: day_validator,
    HOUR: hour_validator,
    MINUTE: minute_validator,
    SECOND: second_validator,

    # Miscellaneous validators.
    ISNULL: isnull_validator,
}
