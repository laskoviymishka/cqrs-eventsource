from setuptools import find_packages, setup
from eventsource import __version__

long_description = """
This package provides generic support for async event sourcing in Python.

`Please raise issues on GitHub <https://github.com/laskoviymishka/cqrs-eventsource/issues>`_.
"""

packages = find_packages(
    exclude=[
    ]
)

setup(
    name='eventsourcing_async',
    version=__version__,
    description='Event sourcing async in Python',
    author='John Bywater',
    author_email='andrei_tserakhau@epam.com',
    url='https://github.com/laskoviymishka/cqrs-eventsource',
    packages=packages,
    install_requires=[
        'six<=1.10.99999',
        'python-dateutil',
        'peewee',
        'peewee_async',
        'aiounittest',
        'aiopg',
        'asynctest',
    ],
    zip_safe=False,
    long_description=long_description,
    keywords=['event sourcing', 'event store', 'async', 'domain driven design', 'ddd', 'cqrs', 'cqs'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
