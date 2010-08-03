#!/usr/bin/env python

try:
    import setuptools

except ImportError:
    import distribute_setup
    distribute_setup.use_setuptools()

from setuptools import setup
import sys

VERSION = '0.8.1'
DESCRIPTION = "Python module dependency analysis tool"
LONG_DESCRIPTION = """
modulegraph determines a dependency graph between Python modules primarily
by bytecode analysis for import statements.

modulegraph uses similar methods to modulefinder from the standard library,
but uses a more flexible internal representation, has more extensive 
knowledge of special cases, and is extensible.

NEWS
====

0.8.1
-----

This is a minor feature release

Features:

- ``from __future__ import absolute_import`` is now supported

- Relative imports (``from . import module``) are now supported

- Add support for namespace packages when those are installed
  using option ``--single-version-externally-managed`` (part
  of setuptools/distribute)

0.8
---

This is a minor feature release

Features:

- Initial support for Python 3.x

- It is now possible to run the test suite
  using ``python setup.py test``.

  (The actual test suite is still fairly minimal though)
"""

CLASSIFIERS = filter(None, map(str.strip,
"""                 
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Programming Language :: Python
Programming Language :: Python :: 2
Programming Language :: Python :: 3
Topic :: Software Development :: Libraries :: Python Modules
Topic :: Software Development :: Build Tools
""".splitlines()))

if sys.version_info[0] == 3:
    extra_args = dict(use_2to3=True)
else:
    extra_args = dict()



setup(
    name="modulegraph",
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    classifiers=CLASSIFIERS,
    author="Bob Ippolito",
    author_email="bob@redivi.com",
    maintainer="Ronald Oussoren",
    maintainer_email="ronaldoussoren@mac.com",
    url="http://undefined.org/python/#modulegraph",
    license="MIT License",
    packages=['modulegraph'],
    platforms=['any'],
    install_requires=["altgraph>=0.7"],
    zip_safe=True,
    test_suite='testsuite',
    **extra_args
)
