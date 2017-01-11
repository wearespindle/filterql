import simplejson as json

from .exceptions import InvalidFormat, UnsupportedLookupException
from .lookup_types import EXACT, LOOKUP_TYPES
from .utils import ENCODERS, type_decoder, TypeEncoder
from .validators import VALIDATORS


KEY_PREFIX = '_'
FIELD_KEY = '%sfield' % KEY_PREFIX
LOOKUP_KEY = '%slookup' % KEY_PREFIX
VALUE_KEY = '%svalue' % KEY_PREFIX
TYPE_KEY = '%stype' % KEY_PREFIX


class LookupNode(object):
    """
    Node used for lookups. Has filters that can be either a dict with
    the given filter or another lookup node that contains more filters.
    """
    AND = '%sand' % KEY_PREFIX
    OR = '%sor' % KEY_PREFIX
    NOT = '%snot' % KEY_PREFIX
    default = AND

    def __init__(self, filters=None, connector=None, negated=False):
        """
        Constructs a new Node. With AND as default connector.
        """
        if not isinstance(filters, list) and filters is not None:
            raise TypeError('filters should be list or none')

        if connector not in (self.AND, self.OR) and connector is not None:
            raise TypeError('connector can only be `%s`, `%s` or `None`' % self.AND, self.OR)

        if not isinstance(negated, bool):
            raise TypeError('negated can only be of type bool')

        self.filters = filters[:] if filters else []
        self.connector = connector or self.default
        self.negated = negated

    def to_dict(self):
        """
        Function to transform the node and children into a dict recursively.

        Returns:
            dict: Dict of nodes and filters.
        """
        tree_dict = {}
        tree_dict[self.connector] = [f if isinstance(f, dict) else f.to_dict() for f in self.filters]

        if self.negated:
            return {self.NOT: tree_dict}

        return tree_dict

    def dumps(self):
        """
        Dump this node and children to json.

        Returns:
            string: The json string representing the lookup.
        """
        return json.dumps(self.to_dict(), cls=TypeEncoder, use_decimal=True)

    @staticmethod
    def from_json(l_json):
        """
        Function to create an instance from json.

        Args:
            l_json (string): The json string representing a lookup.

        Returns:
            LookupNode: The lookup instance based on the dict.
        """
        return L.from_dict(json.loads(l_json, object_hook=type_decoder, use_decimal=True))

    @staticmethod
    def from_dict(l_dict):
        """
        Function to create an instance from a dict.

        Args:
            l_dict (dict): The dict that represents a lookup.

        Returns:
            LookupNode: The lookup instance based on the dict.

        Raises:
            InvalidFormat: When the dict is not of the Lookup format.
        """
        # Set some defaults.
        negated = False
        connector = L.AND
        children = []

        # Check for valid formatting and get root connector key.
        keys = list(l_dict)
        if len(keys) != 1:
            raise InvalidFormat('Lookup root can only have 1 key %s' % l_dict)
        connector = keys[0]

        # Check if we have a `not` connector.
        if connector == L.NOT:
            negated = True
            # Get the `and` or `or` connector for the `not` connector.
            l_dict = l_dict.get(L.NOT)
            keys = list(l_dict)
            if len(keys) != 1:
                raise InvalidFormat('Lookup root can only have 1 key %s' % l_dict)
            connector = keys[0]

        # Check for (remaining) valid connector types.
        if connector not in [L.OR, L.AND]:
            raise InvalidFormat(
                'Lookup root connector must be `%s`, `%s` or `%s` %s' % (L.AND, L.NOT, L.OR, l_dict))

        filters = l_dict.get(connector)

        # Loop all filters in the lookup node.
        for _filter in filters:
            # Check if we have a filter or a nested lookup.
            valid_filter_keys = [FIELD_KEY, LOOKUP_KEY, VALUE_KEY]
            valid_type_filter_keys = valid_filter_keys + [TYPE_KEY]
            filter_keys = set(list(_filter))

            if len(filter_keys) == 1 and next(iter(filter_keys)) in (L.AND, L.OR, L.NOT):
                children.append(L.from_dict(_filter))
            elif (filter_keys == set(valid_filter_keys) or
                    filter_keys == set(valid_type_filter_keys)):
                children.append(_filter)
            else:
                raise InvalidFormat('Not a lookup or node for filter %s' % _filter)

        lookup = LookupNode()
        lookup.filters = children
        lookup.connector = connector
        lookup.negated = negated

        return lookup

    def __len__(self):
        """
        The number of filters in the node.
        """
        return len(self.filters)

    def add(self, other_l, conn_type):
        """
        Function to add a node to this node. Try to squash under certain
        conditions or just append them.

        Args:
            other_l (Lookup|LookupNode): The leaf/node to add to self..
            conn_type (string): The connector used in the adding.

        Returns:
            (Lookup|LookupNode): The result of the adding or squashing.
        """
        # Try to avoid double filters and combine nothing.
        if isinstance(other_l, Lookup) and other_l.filters[0] in self.filters:
            return

        # Try to squash filters when we can. When len of the filters of other
        # is 1 it does not matter what the connector of the other_l is. The
        # other_l is of the type Lookup and thus the connector is still
        # the default and subject to change either way.
        if (not other_l.negated and (other_l.connector == conn_type or len(other_l) == 1)):
            self.filters.extend(other_l.filters)
        else:
            self.filters.append(other_l)

    def negate(self):
        """
        Negate the sense of the root connector.
        """
        self.negated = not self.negated

    def _combine(self, other, connector):
        """
        Combine two lookups into one node.

        Args:
            other (Lookup|LookupNode): The other object to combine with.
            connector (string): The connector used for the combining.

        Returns:
            LookupNode: The created node with the combined lookups.
        """
        if not isinstance(other, LookupNode):
            raise TypeError(other)

        obj = LookupNode(connector=connector)
        obj.add(self, connector)
        obj.add(other, connector)
        return obj

    def __or__(self, other):
        return self._combine(other, self.OR)

    def __and__(self, other):
        return self._combine(other, self.AND)

    def __invert__(self):
        obj = type(self)()
        obj.add(self, self.AND)
        obj.negate()
        return obj


class Lookup(LookupNode):
    """
    Class that creates the needed filters and is used as `leaf` for
    a node.
    """
    def __init__(self, field, value, lookup=EXACT, validate=True):
        """
        Validate the given args and init the lookup.
        """
        if validate:
            self._validate_lookup(lookup)
            self._validate_value(value, lookup)

        self.value = value
        self.field = field
        self.lookup = lookup

        total_filter = {
            FIELD_KEY: self.field,
            LOOKUP_KEY: self.lookup,
            VALUE_KEY: self.value,
        }

        if type(value) in list(ENCODERS):
            total_filter[TYPE_KEY] = type(value).__name__

        super(type(self), self).__init__(filters=[total_filter])

    def _validate_lookup(self, lookup):
        """
        Validate whether a supported lookup type is provided.

        Args:
            lookup (string): The lookup type to check.

        Raises:
            UnsupportedLookupException
        """
        if lookup not in LOOKUP_TYPES:
            raise UnsupportedLookupException(lookup)

    def _validate_value(self, value, lookup):
        """
        Validate value based on lookup type.

        Args:
            value (type): The value to validate.
            lookup (string): One of the LOOKUP_TYPES to validate the value for.

        Raises:
            InvalidValueException
        """
        validate = VALIDATORS.get(lookup)
        if validate:
            validate(value)

    def __invert__(self):
        obj = type(self)(self.field, self.value, self.lookup)
        obj.negate()
        return obj


L = Lookup
