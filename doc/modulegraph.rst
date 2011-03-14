:mod:`modulegraph.modulegraph` --- Find modules used by a script
================================================================

.. module:: modulegraph.modulegraph
   :synopsis: Find modules used by a script

This module defines :class:`ModuleGraph`, which is used to find
the dependencies of scripts using bytecode analysis.

A number of APIs in this module refer to filesystem path. Those paths can refer to
files inside zipfiles (for example when there are zipped egg files on :data:`sys.path`).
Filenames referring to entries in a zipfile are not marked any way, if ``"somepath.zip"``
refers to a zipfile, that is ``"somepath.zip/embedded/file"`` will be used to refer to
``embedded/file`` inside the zipfile.

The actual graph
----------------

.. class:: ModuleGraph([path[, excludes[, replace_paths[, implies[, graph[, debug]]]]]])

   Create a new ModuleGraph object. Use the :meth:`run_script` method to add scripts,
   and their dependencies to the graph.

   :param path: Python search path to use, defaults to :data:`sys.path`
   :param excludes: Iterable with module names that should not be included as a dependency
   :param replace_paths: List of pathname rewrites ``(old, new)``. When this argument is
     supplied the ``co_filename`` attributes of code objects get rewritten before scanning
     them for dependencies.
   :param implies: Implied module dependencies, a mapping from a module name to the list
     of modules it depends on. Use this to tell modulegraph about dependencies that cannot
     be found by code inspection (such as imports from C code or using the :func:`__import__`
     function).
   :param graph: A precreated :class:`Graph <altgraph.Graph.Graph>` object to use, the 
     default is to create a new one.
   :param debug: The :class:`ObjectGraph <altgraph.ObjectGraph.ObjectGraph>` debug level.


.. method:: run_script(pathname[, caller])

   Create a node by path (not module name). The *pathname* should refer to a Python
   source file and will be scanned for dependencies.

   The optional argument *caller* is the the node that calls this script,
   and is used to add a reference in the graph.

.. method:: import_hook(name[, caller[, fromlist[, level]]])

   Import a module and analyse its dependencies

   :args name:     The module name
   :args caller:   The node that caused the import to happen
   :args fromlist: The list of names to import, this is an empty list for
      ``import name`` and a list of names for ``from name import a, b, c``.
   :args level:    The import level. The value should be ``0`` for classical Python 2
     imports, ``-1`` for absolute imports and a positive number for relative imports (
     where the value is the number of leading dots in the imported name).


.. method:: implyNodeReference(node, other)

   Imply that one *node* depends on an *other* node. The *other*
   argument is either a :class:`Node`, or the name of a node.

   Use this for imports by extension modules and tricky import code.

.. method:: createReference(fromnode, tonode[, edge_data])

   Create a reference from *fromnode* to *tonode*, with optional edge data.

   The default for *edge_data* is ``"direct"``.

.. method:: findNode(name)

   Find a node by identifier.  If a node by that identifier exists, it will be returned.

   If a lazy node exists by that identifier with no dependencies (excluded), it will be 
   instantiated and returned.

   If a lazy node exists by that identifier with dependencies, it and its
   dependencies will be instantiated and scanned for additional depende

.. method:: create_xref([out])

   Write an HTML file to the *out* stream (defaulting to :data:`sys.stdout`).

   The HTML file contains a textual description of the dependency graph.

.. method:: graphreport([fileobj[, flatpackages]])

   .. todo:: To be documented

.. method:: report()

   Print a report to stdout, listing the found modules with their
   paths, as well as modules that are missing, or seem to be missing.


Mostly internal methods
.......................

The methods in this section should be considered as methods for subclassing at best,
please let us know if you need these methods in your code as they are on track to be
made private methods before the 1.0 release.

.. method:: determine_parent(caller)

   Returns package node that contains the *caller*. Returns :data:`None` when
   *caller* is not in a package, or is itself :data:`None`.

.. method:: find_head_package(parent, name[, level])

   .. todo:: To be documented

.. method:: load_tail(q, tail)

   .. todo:: To be documented

.. method:: ensure_fromlist(m, fromlist)

   .. todo: To be documented

.. method:: find_all_submodules(m)

   Yield the module info for submodules of in the same package as *m*.

.. method:: import_module(partname, fqname, parent)

   .. todo: To be documented

.. method:: load_module(fqname, fp, pathname, (suffix, mode, type))

   .. todo: To be documented

.. method:: scan_code(code, m)

   Scan the *code* object for module *m* and update the dependencies of
   *m* using the import statemets found in the code. 
   
   This will automaticly scan the code for nested functions, generator
   expressions and list comprehensions as well.

.. method:: load_package(fqname, pathname)

   Load a package directory.

.. method:: find_module(name, path[, parent])

   .. todo:: To be documented


.. method:: itergraphreport([name[, flatpackages]])

   .. todo:: To be documented

.. method:: replace_paths_in_code(co)

   Replace the filenames in code object *co* using the *replace_paths* value that
   was passed to the contructor. Returns the rewritten code object.

Graph nodes
-----------

The :class:`ModuleGraph` contains nodes that represent the various types of modules.

.. class:: Alias(value)

   This is a subclass of string that is used to mark module aliases.

.. class:: Node(identifier)

   Base class for nodes.

   .. todo:: add documentation

.. class:: AliasNode (name, node)

   A node that represents an alias from a name to another node.

.. class:: BadModule(identifier)

   Base class for nodes that should be ignored for some reason

.. class:: ExcludedModule(identifier)

   A module that is explicitly excluded.

.. class:: MissingModule(identifier)

   A module that is imported but cannot be located.

.. class:: Script(filename)

   A python script.

   .. data:: filename

      The filename for the script

.. class:: BaseModule(name[, filename[, path]])

    The base class for actual modules. The *name* is
    the possibly dotted module name, *filename* is the
    filesystem path to the module and *path* is the
    value of ``__path__`` for the module.

    .. data:: identifier

       The name of the module

    .. data:: filename

       The filesystem path to the module.

    .. data:: path

       The value of ``__path__`` for this module.

.. class:: BuiltinModule(name)

   A built-in module (on in :data:`sys.builtin_module_names`).

.. class:: SourceModule(name)

   A module for which the python source code is available.

.. class:: CompiledModule(name)

   A module for which only byte-code is available.

.. class:: Package(name)

   Represents a python package

.. class:: Extension(name)

   A native extension


.. warning:: A number of other node types are defined in the module. Those modules aren't
   used by modulegraph and will be removed in a future version.



Utility functions
-----------------

.. function:: find_module(name[, path])

   A version of :func:`imp.find_module` that works with zipped packages (and other
   :pep:`302` importers).

.. function:: moduleInfoForPath(path)

   Return the module name, readmode and type for the file at *path*, or
   None if it doesn't seem to be a valid module (based on its name).

.. function:: addPackagePath(packagename, path)

   Add *path* to the value of ``__path__`` for the package named *packagename*.

.. function:: replacePackage(oldname, newname)

   Rename *oldname* to *newname* when it is found by the module finder. This
   is used as a workaround for the hack that the ``_xmlplus`` package uses
   to inject itself in the ``xml`` namespace.


