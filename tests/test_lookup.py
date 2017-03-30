from datetime import date

from pytest import raises
import simplejson as json

from filterql.exceptions import InvalidFormat, InvalidValueException, UnsupportedLookupException
from filterql import ISNULL, L
from filterql.lookup import FIELD_KEY, LookupNode, LOOKUP_KEY, TYPE_KEY, VALUE_KEY
from filterql.lookup_types import LOOKUP_TYPES


def test_invalid_lookup_type():
    """
    Test a lookup with a invalid type.
    """
    message = '`spindle` is not a supported lookup! Supported lookups are: %s' % LOOKUP_TYPES

    with raises(UnsupportedLookupException) as excinfo:
        L('name', 'spindle', lookup='spindle')

    assert str(excinfo.value) == message


def test_invalid_value_for_lookup():
    """
    Test invalid value for a lookup.
    """
    message = 'Only True or False allowed for ISNULL lookup type.'

    with raises(InvalidValueException) as excinfo:
        L('name', 'null', lookup=ISNULL)

    assert str(excinfo.value) == message


def test_dumps():
    """
    Test dumping of a lookup.
    """
    # The JSON dumps is unordered so try all possible combinations.
    lookup = L('name', 'spindle')
    result = lookup.dumps()

    assert lookup.to_dict() == json.loads(result)
    assert lookup.to_dict() == L.from_json(result).to_dict()


def test_combining_invalid_types():
    """
    Test combining invalid types.
    """
    with raises(TypeError):
        L('name', 'spindle') & 1337


def test_lookup_node_kwarg_validation():
    """
    Test invalid types for LookupNode init.
    """
    with raises(TypeError):
        LookupNode(filters='x')

    with raises(TypeError):
        LookupNode(connector='hello')

    with raises(TypeError):
        LookupNode(negated='yes')


def test_one_lookup():
    """
    Test one normal lookup.
    """
    lookup = L('name', 'spindle')
    expected = {
        L.AND: [
            {FIELD_KEY: 'name', VALUE_KEY: 'spindle', LOOKUP_KEY: 'exact'},
        ]
    }

    assert lookup.to_dict() == expected


def test_one_not_lookup():
    """
    Test one `not` lookup.
    """
    lookup = ~L('name', 'spindle')
    expected = {
        L.NOT: {
            L.AND: [
                {FIELD_KEY: 'name', VALUE_KEY: 'spindle', LOOKUP_KEY: 'exact'},
            ]
        }
    }

    assert lookup.to_dict() == expected


def test_and_lookup():
    """
    Test the `and` lookup.
    """
    lookup = L('name', 'spindle') & L('country', 'netherlands')
    expected = {
        L.AND: [
            {FIELD_KEY: 'name', VALUE_KEY: 'spindle', LOOKUP_KEY: 'exact'},
            {FIELD_KEY: 'country', VALUE_KEY: 'netherlands', LOOKUP_KEY: 'exact'},
        ]
    }

    assert lookup.to_dict() == expected

    lookup = L('name', 'spindle') & L('country', 'netherlands') & L('status', 'awesome')
    expected = {
        L.AND: [
            {FIELD_KEY: 'name', VALUE_KEY: 'spindle', LOOKUP_KEY: 'exact'},
            {FIELD_KEY: 'country', VALUE_KEY: 'netherlands', LOOKUP_KEY: 'exact'},
            {FIELD_KEY: 'status', VALUE_KEY: 'awesome', LOOKUP_KEY: 'exact'},
        ]
    }

    assert lookup.to_dict() == expected


def test_or_lookup():
    """
    Test the `or` lookup.
    """
    lookup = L('name', 'spindle') | L('name', 'devhouse')
    expected = {
        L.OR: [
            {FIELD_KEY: 'name', VALUE_KEY: 'spindle', LOOKUP_KEY: 'exact'},
            {FIELD_KEY: 'name', VALUE_KEY: 'devhouse', LOOKUP_KEY: 'exact'},
        ]
    }

    assert lookup.to_dict() == expected

    lookup = L('name', 'spindle') | L('name', 'devhouse') | L('name', 'devhouse spindle')
    expected = {
        L.OR: [
            {FIELD_KEY: 'name', VALUE_KEY: 'spindle', LOOKUP_KEY: 'exact'},
            {FIELD_KEY: 'name', VALUE_KEY: 'devhouse', LOOKUP_KEY: 'exact'},
            {FIELD_KEY: 'name', VALUE_KEY: 'devhouse spindle', LOOKUP_KEY: 'exact'},
        ]
    }

    assert lookup.to_dict() == expected


def test_one_not_and_lookup():
    """
    Test one normal and one `not` lookup.
    """
    lookup = L('name', 'spindle') & ~L('country', 'netherlands')
    expected = {
        L.AND: [
            {FIELD_KEY: 'name', VALUE_KEY: 'spindle', LOOKUP_KEY: 'exact'},
            {L.NOT: {
                L.AND: [
                    {FIELD_KEY: 'country', VALUE_KEY: 'netherlands', LOOKUP_KEY: 'exact'},
                ]
            }},
        ]
    }

    assert lookup.to_dict() == expected


def test_all_not_and_lookup():
    """
    Test all lookups with `not`.
    """
    lookup = ~(L('name', 'spindle') & L('country', 'netherlands'))
    expected = {
        L.NOT: {
            L.AND: [
                {FIELD_KEY: 'name', VALUE_KEY: 'spindle', LOOKUP_KEY: 'exact'},
                {FIELD_KEY: 'country', VALUE_KEY: 'netherlands', LOOKUP_KEY: 'exact'},
            ]
        }
    }

    assert lookup.to_dict() == expected

    lookup = ~(L('name', 'spindle') & L('country', 'netherlands') & L('status', 'awesome'))
    expected = {
        L.NOT: {
            L.AND: [
                {FIELD_KEY: 'name', VALUE_KEY: 'spindle', LOOKUP_KEY: 'exact'},
                {FIELD_KEY: 'country', VALUE_KEY: 'netherlands', LOOKUP_KEY: 'exact'},
                {FIELD_KEY: 'status', VALUE_KEY: 'awesome', LOOKUP_KEY: 'exact'},
            ]
        }
    }

    assert lookup.to_dict() == expected


def test_and_or_lookup():
    """
    Test lookup with the use of `and` and `or`.
    """
    lookup = L('name', 'spindle') & L('country', 'netherlands') | L('status', 'awesome')
    expected = {
        L.OR: [
            {L.AND: [
                {FIELD_KEY: 'name', VALUE_KEY: 'spindle', LOOKUP_KEY: 'exact'},
                {FIELD_KEY: 'country', VALUE_KEY: 'netherlands', LOOKUP_KEY: 'exact'},
            ]},
            {FIELD_KEY: 'status', VALUE_KEY: 'awesome', LOOKUP_KEY: 'exact'},
        ]
    }

    assert lookup.to_dict() == expected

    lookup = L('status', 'awesome') | L('name', 'spindle') & L('country', 'netherlands')
    expected = {
        L.OR: [
            {FIELD_KEY: 'status', VALUE_KEY: 'awesome', LOOKUP_KEY: 'exact'},
            {L.AND: [
                {FIELD_KEY: 'name', VALUE_KEY: 'spindle', LOOKUP_KEY: 'exact'},
                {FIELD_KEY: 'country', VALUE_KEY: 'netherlands', LOOKUP_KEY: 'exact'},
            ]},
        ]
    }

    assert lookup.to_dict() == expected


def test_complex_mix_lookup():
    """
    Test two complex mixed lookups with `not's` `and's` and `or's`.
    """
    lookup = (~L('name', 'spindle') & L('status', 'awesome')) & (L('country', 'netherlands') | L('country', 'germany'))
    expected = {
        L.AND: [
            {L.NOT: {L.AND: [
                {FIELD_KEY: 'name', VALUE_KEY: 'spindle', LOOKUP_KEY: 'exact'},
            ]}},
            {FIELD_KEY: 'status', VALUE_KEY: 'awesome', LOOKUP_KEY: 'exact'},
            {L.OR: [
                {FIELD_KEY: 'country', VALUE_KEY: 'netherlands', LOOKUP_KEY: 'exact'},
                {FIELD_KEY: 'country', VALUE_KEY: 'germany', LOOKUP_KEY: 'exact'},
            ]},
        ]
    }

    assert lookup.to_dict() == expected

    lookup = (L('name', 'spindle') & L('status', 'awesome')) | ~(L('country', 'netherlands') | L('country', 'germany'))
    expected = {
        L.OR: [
            {L.AND: [
                {FIELD_KEY: 'name', VALUE_KEY: 'spindle', LOOKUP_KEY: 'exact'},
                {FIELD_KEY: 'status', VALUE_KEY: 'awesome', LOOKUP_KEY: 'exact'},
            ]},
            {L.NOT: {L.AND: [{L.OR: [
                {FIELD_KEY: 'country', VALUE_KEY: 'netherlands', LOOKUP_KEY: 'exact'},
                {FIELD_KEY: 'country', VALUE_KEY: 'germany', LOOKUP_KEY: 'exact'},
            ]}]}},
        ]
    }

    assert lookup.to_dict() == expected


def test_duplicate_lookup():
    """
    Test when combining exactly the same lookups.
    """
    lookup = L('name', 'spindle') & L('name', 'spindle')
    expected = {
        L.AND: [
            {FIELD_KEY: 'name', VALUE_KEY: 'spindle', LOOKUP_KEY: 'exact'},
        ]
    }

    assert lookup.to_dict() == expected

    lookup = L('name', 'spindle') & L('name', 'spindle') & L('name', 'spindle')

    assert lookup.to_dict() == expected


def test_invalid_formats():
    """
    Test supplying invalid formats to from_dict.
    """
    wrong_format = {L.AND: '', L.OR: ''}
    message = 'Lookup root can only have 1 key %s' % wrong_format

    with raises(InvalidFormat) as execinfo:
        L.from_dict(wrong_format)

    assert str(execinfo.value) == message

    wrong_format = {L.NOT: {L.AND: '', L.OR: ''}}
    message = 'Lookup root can only have 1 key %s' % {L.AND: '', L.OR: ''}

    with raises(InvalidFormat) as execinfo:
        L.from_dict(wrong_format)

    assert str(execinfo.value) == message

    wrong_format = {'unknown': ''}
    message = 'Lookup root connector must be `%s`, `%s` or `%s` %s' % (L.AND, L.NOT, L.OR, wrong_format)

    with raises(InvalidFormat) as execinfo:
        L.from_dict(wrong_format)

    assert str(execinfo.value) == message

    wrong = {L.AND: 'wrong', L.OR: 'format'}
    wrong_format = {L.AND: [wrong]}
    message = 'Not a lookup or node for filter %s' % wrong

    with raises(InvalidFormat) as execinfo:
        L.from_dict(wrong_format)

    assert str(execinfo.value) == message


def test_adding_type_to_filter():
    """
    Test if type is added to filter for unsupported json types.
    """
    lookup = L('date', date(2017, 6, 6))

    _filter = lookup.filters[0]
    _type = _filter.get(TYPE_KEY)

    assert _type
    assert _type == date.__name__
