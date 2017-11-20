# Event Sourcing in Python

[![Build Status](https://secure.travis-ci.org/johnbywater/eventsourcing.png)](https://travis-ci.org/johnbywater/eventsourcing)
[![Coverage Status](https://coveralls.io/repos/github/johnbywater/eventsourcing/badge.svg)](https://coveralls.io/github/johnbywater/eventsourcing)
[![Gitter chat](https://badges.gitter.im/gitterHQ/services.png)](https://gitter.im/eventsourcing-in-python/eventsourcing)

A library for event sourcing in Python.

## Installation

Use pip to install the [stable distribution](https://pypi.python.org/pypi/eventsourcing) from
the Python Package Index.

    pip install eventsourcing-async


## Documentation

Each application start with domain, so lets create a domain aggregate root:

```python

class ToDoAggregate(AggregateRoot):
    pass

```


## Project

This project is [hosted on GitHub](https://github.com/laskoviymishka/cqrs-eventsource).
Please [register your questions, requests and any other issues](https://github.com/laskoviymishka/cqrs-eventsource/issues).
