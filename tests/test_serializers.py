from django.db.models import Q

from filterql import ISNULL, L
from filterql.serializers import DjangoSerializer


def _do_compare(result, expected):
    """
    Recursively compare nested Q objects.

    Args:
        result (Q): The result from deserialization.
        expected (Q): The expected Q object.
    """
    assert result.negated == expected.negated
    assert result.connector == expected.connector
    for index, child in enumerate(result.children):
        if isinstance(child, Q):
            _do_compare(child, expected.children[index])
        else:
            assert child == expected.children[index]


def _do_comparison_test(lookup, expected):
    """
    Compare crucial elements of the result and expected Q objects.

    Args:
        lookup (L): The lookup to deserialize.
        expected (Q): The expected Q object.
    """
    lookup_json = lookup.dumps()
    result = DjangoSerializer().from_json(lookup_json)

    _do_compare(result, expected)

    assert str(result) == str(expected)


def test_one_lookup():
    """
    Test one normal lookup.
    """
    lookup = L('name', 'spindle')
    expected = Q(name='spindle')

    _do_comparison_test(lookup, expected)

    lookup = L('name', True, lookup=ISNULL)
    expected = Q(name__isnull=True)

    _do_comparison_test(lookup, expected)


def test_one_not_lookup():
    """
    Test one `not` lookup.
    """
    lookup = ~L('name', 'spindle')
    expected = ~Q(name='spindle')

    _do_comparison_test(lookup, expected)


def test_and_lookup():
    """
    Test the `and` lookup.
    """
    lookup = L('name', 'spindle') & L('country', 'netherlands')
    expected = Q(name='spindle') & Q(country='netherlands')

    _do_comparison_test(lookup, expected)

    lookup = L('name', 'spindle') & L('country', 'netherlands') & L('status', 'awesome')
    expected = Q(name='spindle') & Q(country='netherlands') & Q(status='awesome')

    _do_comparison_test(lookup, expected)


def test_or_lookup():
    """
    Test the `or` lookup.
    """
    lookup = L('name', 'spindle') | L('name', 'devhouse')
    expected = Q(name='spindle') | Q(name='devhouse')

    _do_comparison_test(lookup, expected)

    lookup = L('name', 'spindle') | L('name', 'devhouse') | L('name', 'devhouse spindle')
    expected = Q(name='spindle') | Q(name='devhouse') | Q(name='devhouse spindle')

    _do_comparison_test(lookup, expected)


def test_one_not_and_lookup():
    """
    Test one normal and one `not` lookup.
    """
    lookup = L('name', 'spindle') & ~L('country', 'netherlands')
    expected = Q(name='spindle') & ~Q(country='netherlands')

    _do_comparison_test(lookup, expected)


def test_all_not_and_lookup():
    """
    Test all lookups with `not`.
    """
    lookup = ~(L('name', 'spindle') & L('country', 'netherlands'))
    expected = ~(Q(name='spindle') & Q(country='netherlands'))

    _do_comparison_test(lookup, expected)

    lookup = ~(L('name', 'spindle') & L('country', 'netherlands') & L('status', 'awesome'))
    expected = ~(Q(name='spindle') & Q(country='netherlands') & Q(status='awesome'))

    _do_comparison_test(lookup, expected)


def test_and_or_lookup():
    """
    Test lookup with the use of `and` and `or`.
    """
    lookup = L('name', 'spindle') & L('country', 'netherlands') | L('status', 'awesome')
    expected = Q(name='spindle') & Q(country='netherlands') | Q(status='awesome')

    _do_comparison_test(lookup, expected)

    lookup = L('status', 'awesome') | L('name', 'spindle') & L('country', 'netherlands')
    expected = Q(status='awesome') | Q(name='spindle') & Q(country='netherlands')

    _do_comparison_test(lookup, expected)


def test_complex_mix_lookup():
    """
    Test two complex mixed lookups with `not's` `and's` and `or's`.
    """
    lookup = (~L('name', 'spindle') & L('status', 'awesome')) & (L('country', 'netherlands') | L('country', 'germany'))
    expected = (~Q(name='spindle') & Q(status='awesome')) & (Q(country='netherlands') | Q(country='germany'))

    _do_comparison_test(lookup, expected)

    lookup = (L('name', 'spindle') & L('status', 'awesome')) | ~(L('country', 'netherlands') | L('country', 'germany'))
    expected = (Q(name='spindle') & Q(status='awesome')) | ~(Q(country='netherlands') | Q(country='germany'))

    _do_comparison_test(lookup, expected)


def test_special_type_lookup():
    """
    Test converting lookups with the special Decimal type.
    """
    pi = '3.141592653589793238462643383279502884197169399375'

    lookup = L('pi', pi)
    expected = Q(pi=pi)

    _do_comparison_test(lookup, expected)
