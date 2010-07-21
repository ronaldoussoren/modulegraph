#!/usr/bin/env python

try:
    import setuptools

except ImportError:
    import distribute_setup
    distribute_setup.use_setuptools()

from setuptools import setup
import sys

VERSION = '0.8'
DESCRIPTION = "Python module dependency analysis tool"
LONG_DESCRIPTION = """
modulegraph determines a dependency graph between Python modules primarily
by bytecode analysis for import statements.

modulegraph uses similar methods to modulefinder from the standard library,
but uses a more flexible internal representation, has more extensive 
knowledge of special cases, and is extensible.
"""

CLASSIFIERS = filter(None, map(str.strip,
"""                 
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Programming Language :: Python
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
    url="http://undefined.org/python/#modulegraph",
    license="MIT License",
    packages=['modulegraph'],
    platforms=['any'],
    install_requires=["altgraph>=0.7"],
    zip_safe=True,
    test_suite='test',
    **extra_args
)
