Release history
===============

0.9
---

This is a minor feature release


Features:

- Documentation is now generated using `sphinx <http://pypi.python.org/pypi/sphinx>`_
  and can be viewed at <http://packages.python.org/modulegraph>.

  The documention is very rough at this moment and in need of reorganisation and
  language cleanup. I've basiclly writting the current version by reading the code
  and documenting what it does, the order in which classes and methods are document
  is therefore not necessarily the most useful. 

- The repository has moved to bitbucket

- Renamed ``modulegraph.modulegraph.AddPackagePath`` to ``addPackagePath``,
  likewise ``ReplacePackage`` is now ``replacePackage``. The old name is still
  available, but is deprecated and will be removed before the 1.0 release.

- ``modulegraph.modulegraph`` contains two node types that are unused and
  have unclear semantics: ``FlatPackage`` and ``ArchiveModule``. These node
  types are deprecated and will be removed before 1.0 is released.

- Added a simple commandline tool (``modulegraph``) that will print information
  about the dependency graph of a script.

- Added a module (``zipio``) for dealing with paths that may refer to entries 
  inside zipfiles (such as source paths referring to modules in zipped eggfiles).

  With this addition ``modulegraph.modulegraph.os_listdir`` is deprecated and
  it will be removed before the 1.0 release.

Bug fixes:

- The ``__cmp__`` method of a Node no longer causes an exception
  when the compared-to object is not a Node. Patch by Ivan Kozik.

- Issue #1: The initialiser for ``modulegraph.ModuleGraph`` caused an exception
  when an entry on the path (``sys.path``) doesn't actually exist.

  Fix by "skurylo", testcase by Ronald.

- The code no longer worked with python 2.5, this release fixes that.

- Due to the switch to mercurial setuptools will no longer include
  all required files. Fixed by adding a MANIFEST.in file

- The method for printing a ``.dot`` representation of a ``ModuleGraph``
  works again.


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
