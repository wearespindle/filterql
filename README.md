# FilterQL

[![Build Status](https://travis-ci.org/wearespindle/filterql.svg?branch=develop)](https://travis-ci.org/wearespindle/filterql)

With FilterQL you can write filter queries with the use of python objects.
These objects can be translated to json and send over the wire to be used
in some other backend. This allows you to not be limited to the way you
can define filters in (front-end) applications that communicate with
and API.

## Status

Currently actively used and watched.

## Usage

### Requirements

 * python 2.7
 * python 3.3, 3.4, 3.5
 * (optional) django >= 1.8

### Installation

```
pip install filterql
```

### Running

```python

from filterql import L, STARTSWITH

# Filter query for name to start with `spindle` or `devhouse`
lookup = L('name', 'spindle', lookup=STARTSWITH) | L('name', 'devhouse', lookup=STARTSWITH)

# Convert to json to be able to send it to other systems.
lookup_json = lookup.dumps()

# On the other side either convert back to L objects or to Django Q objects.

# L
l_filters = L.from_json(lookup_json)

# Django
from filterql.serializers import DjangoSerializer

django_filters = DjangoSerializer().from_json(lookup_json)
```

## Contributing

See the [CONTRIBUTING.md](https://github.com/wearespindle/filterql/blob/develop/CONTRIBUTING.md) file on how to contribute to this project.

## Contributors

See the [CONTRIBUTORS.md](https://github.com/wearespindle/filterql/blob/develop/CONTRIBUTORS.md) file for a list of contributors to the project.

## Roadmap

### Changelog

The changelog can be found in the [CHANGELOG.md](https://github.com/wearespindle/filterql/blob/develop/CHANGELOG.md) file.

### In progress

 * Publish on pypi

### Future

 * Improve logic for combining lookup elements
 * (De)serialization for other data types like XML


## Get in touch with a developer

If you want to report an issue see the [CONTRIBUTING.md](https://github.com/wearespindle/filterql/blob/develop/CONTRIBUTING.md) file for more info.

We will be happy to answer your other questions at opensource@wearespindle.com

## Added something for gitlab

Here is some text for you to review on gitlab. Discussion.
