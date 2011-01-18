Release history
===============

0.8.2
-----

This is a minor feature release


Features:

- Documentation is now generated using `sphinx <http://pypi.python.org/pypi/sphinx>`_
  and can be viewed at <http://packages.python.org/modulegraph>.

- The repository has moved to bitbucket


Bug fixes:

- The ``__cmp__`` method of a Node no longer causes an exception
  when the compared-to object is not a Node. Patch by Ivan Kozik.


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
