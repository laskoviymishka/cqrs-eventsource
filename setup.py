from setuptools import find_packages, setup
from eventsource import __version__


long_description = """
This package provides generic support for event sourcing in Python.

`Package documentation is now available <http://eventsourcing.readthedocs.io/>`_.

`Please raise issues on GitHub <https://github.com/johnbywater/eventsourcing/issues>`_.
"""

packages = find_packages(
    exclude=[
    ]
)

setup(
    name='eventsourcing',
    version=__version__,
    description='Event sourcing in Python',
    author='John Bywater',
    author_email='john.bywater@appropriatesoftware.net',
    url='https://github.com/johnbywater/eventsourcing',
    packages=packages,
    install_requires=[
        'six<=1.10.99999',
        'python-dateutil',
        'peewee',
        'peewee_async',
        'aiounittest',
    ],
    zip_safe=False,
    long_description=long_description,
    keywords=['event sourcing', 'event store', 'domain driven design', 'ddd', 'cqrs', 'cqs'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
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
