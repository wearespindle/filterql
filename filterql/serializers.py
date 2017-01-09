from .lookup import FIELD_KEY, L, LOOKUP_KEY, LookupNode, VALUE_KEY
from .lookup_types import EXACT


class DjangoSerializer():
    """
    Class for (de)serializing L dict or L json to django Q object.
    """
    CONNECTOR_MAP = {
        L.AND: 'AND',
        L.OR: 'OR',
    }

    def __init__(self):
        """
        Lazy set the DJANGO_SUFFIX_DELIMITER based on a Django constant.
        """
        from django.db.models.constants import LOOKUP_SEP
        self.DJANGO_SUFFIX_DELIMITER = LOOKUP_SEP

    def from_json(self, json_string):
        """
        Load a json string into a django Q object.

        Args:
            json_string (string): A valid json string.

        Returns:
            Q: Django Q filter.
        """
        return self.deserialize(L.from_json(json_string))

    def deserialize(self, l_object):
        """
        Deserialize a dict into django Q object.

        Args:
            l_object (LookupNode): The L object to deserialize.

        Returns:
            Q: Django Q filter.
        """
        # Lazy import to avoid conflicts when not using this django serializer.
        from django.db.models import Q

        # Set some defaults.
        negated = l_object.negated
        connector = self.CONNECTOR_MAP[l_object.connector]
        children = []

        filters = l_object.filters

        # Loop all filters in the lookup node.
        for _filter in filters:
            if isinstance(_filter, LookupNode):
                children.append(self.deserialize(_filter))
            else:
                children.append(self._convert_filter(_filter))

        query = Q()
        query.children = children
        query.connector = connector
        query.negated = negated

        return query

    def _convert_filter(self, filter_dict):
        """
        Function to convert the L format of a filter to the django Q format
        of a filter.

        Args:
            filter_dict (dict): Dict with the filter keys and values.

        Returns:
            tuple: With the lookup and the value.
        """
        field = filter_dict[FIELD_KEY]
        value = filter_dict[VALUE_KEY]
        lookup = filter_dict[LOOKUP_KEY]
        if lookup == EXACT:
            lookup = ''
        else:
            lookup = '%s%s' % (self.DJANGO_SUFFIX_DELIMITER, lookup)

        django_lookup = '%s%s' % (field, lookup)

        return (django_lookup, value)
