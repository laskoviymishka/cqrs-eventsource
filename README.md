# Event Sourcing in Python

[![Build Status](https://secure.travis-ci.org/laskoviymishka/cqrs-eventsource.png)](https://travis-ci.org/laskoviymishka/cqrs-eventsource)
[![Coverage Status](https://coveralls.io/repos/github/laskoviymishka/cqrs-eventsource/badge.svg?branch=master)](https://coveralls.io/github/laskoviymishka/cqrs-eventsource?branch=master)


A library for event sourcing in Python.

## Installation

Use pip to install the [stable distribution](https://pypi.python.org/pypi/eventsourcing-async) from
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
