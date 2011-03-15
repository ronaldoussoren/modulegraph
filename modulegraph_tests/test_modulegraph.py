import unittest
from modulegraph import modulegraph
import pkg_resources
import os
import imp
import sys
import warnings
from altgraph import Graph
import textwrap

try:
    bytes
except NameError:
    bytes = str

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

try:
    expectedFailure = unittest.expectedFailure
except AttributeError:
    import functools
    def expectedFailure(function):
        @functools.wraps(function)
        def wrapper(*args, **kwds):
            try:
                function(*args, **kwds)
            except AssertionError:
                pass

            else:
                self.fail("unexpected pass")

class TestFunctions (unittest.TestCase):
    if not hasattr(unittest.TestCase, 'assertIsInstance'):
        def assertIsInstance(self, obj, types):
            self.assertTrue(isinstance(obj, types), '%r is not instance of %r'%(obj, types))

    def test_eval_str_tuple(self):
        for v in [
            '()',
            '("hello",)',
            '("hello", "world")',
            "('hello',)",
            "('hello', 'world')",
            "('hello', \"world\")",
            ]:

            self.assertEqual(modulegraph._eval_str_tuple(v), eval(v))

        self.assertRaises(ValueError, modulegraph._eval_str_tuple, "")
        self.assertRaises(ValueError, modulegraph._eval_str_tuple, "'a'")
        self.assertRaises(ValueError, modulegraph._eval_str_tuple, "'a', 'b'")
        self.assertRaises(ValueError, modulegraph._eval_str_tuple, "('a', ('b', 'c'))")
        self.assertRaises(ValueError, modulegraph._eval_str_tuple, "('a', ('b\", 'c'))")

    def test_namespace_package_path(self):
        class DS (object):
            def __init__(self, path, namespace_packages=None):
                self.location = path
                self._namespace_packages = namespace_packages

            def has_metadata(self, key):
                if key == 'namespace_packages.txt':
                    return self._namespace_packages is not None

                raise ValueError("invalid lookup key")

            def get_metadata(self, key):
                if key == 'namespace_packages.txt':
                    if self._namespace_packages is None:
                        raise ValueError("no file")

                    return self._namespace_packages 

                raise ValueError("invalid lookup key")

        class WS (object):
            def __iter__(self):
                yield DS("/pkg/pkg1")
                yield DS("/pkg/pkg2", "foo\n")
                yield DS("/pkg/pkg3", "bar.baz\n")
                yield DS("/pkg/pkg4", "foobar\nfoo\n")

        saved_ws = pkg_resources.working_set
        try:
            pkg_resources.working_set = WS()

            self.assertEqual(modulegraph._namespace_package_path("sys", "appdir/pkg"), ["appdir/pkg"])
            self.assertEqual(modulegraph._namespace_package_path("foo", "appdir/pkg"), ["/pkg/pkg2/foo", "/pkg/pkg4/foo"])
            self.assertEqual(modulegraph._namespace_package_path("bar.baz", "appdir/pkg"), ["/pkg/pkg3/bar/baz"])

        finally:
            pkg_resources.working_set = saved_ws

    def test_os_listdir(self):
        root = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 'testdata')

        self.assertEqual(modulegraph.os_listdir('/etc/'), os.listdir('/etc'))
        self.assertRaises(IOError, modulegraph.os_listdir, '/etc/hosts/foobar')
        self.assertRaises(IOError, modulegraph.os_listdir, os.path.join(root, 'test.egg', 'bar'))

        self.assertEqual(list(sorted(modulegraph.os_listdir(os.path.join(root, 'test.egg', 'foo')))),
            [ 'bar', 'bar.txt', 'baz.txt' ])

    def test_code_to_file(self):
        try:
            code = modulegraph._code_to_file.__code__
        except AttributeError:
            code = modulegraph._code_to_file.func_code

        data = modulegraph._code_to_file(code)
        self.assertTrue(hasattr(data, 'read'))

        content = data.read()
        self.assertIsInstance(content, bytes)
        data.close()

    @expectedFailure
    def test_find_module(self):
        self.fail("Missing test for modulegraph.find_module")

    def test_moduleInfoForPath(self):
        self.assertEqual(modulegraph.moduleInfoForPath("/somewhere/else/file.txt"), None)

        info = modulegraph.moduleInfoForPath("/somewhere/else/file.py")
        self.assertEqual(info[0], "file")
        self.assertEqual(info[1], "U")
        self.assertEqual(info[2], imp.PY_SOURCE)

        info = modulegraph.moduleInfoForPath("/somewhere/else/file.pyc")
        self.assertEqual(info[0], "file")
        self.assertEqual(info[1], "rb")
        self.assertEqual(info[2], imp.PY_COMPILED)

        if sys.platform in ('darwin', 'linux2'):
            info = modulegraph.moduleInfoForPath("/somewhere/else/file.so")
            self.assertEqual(info[0], "file")
            self.assertEqual(info[1], "rb")
            self.assertEqual(info[2], imp.C_EXTENSION)

        elif sys.platform in ('win32',):
            info = modulegraph.moduleInfoForPath("/somewhere/else/file.pyd")
            self.assertEqual(info[0], "file")
            self.assertEqual(info[1], "rb")
            self.assertEqual(info[2], imp.C_EXTENSION)

    if sys.version_info[:2] > (2,5):
        exec(textwrap.dedent('''\
            def test_deprecated(self):
                saved_add = modulegraph.addPackagePath
                saved_replace = modulegraph.replacePackage
                try:
                    called = []
                    
                    def log_add(*args, **kwds):
                        called.append(('add', args, kwds))
                    def log_replace(*args, **kwds):
                        called.append(('replace', args, kwds))

                    modulegraph.addPackagePath = log_add
                    modulegraph.replacePackage = log_replace

                    with warnings.catch_warnings(record=True) as w:
                        warnings.simplefilter("always")
                        modulegraph.ReplacePackage('a', 'b')
                        modulegraph.AddPackagePath('c', 'd')

                    self.assertEqual(len(w), 2)
                    self.assertTrue(w[-1].category is DeprecationWarning)
                    self.assertTrue(w[-2].category is DeprecationWarning)

                    self.assertEqual(called, [
                        ('replace', ('a', 'b'), {}),
                        ('add', ('c', 'd'), {}),
                    ])

                finally:
                    modulegraph.addPackagePath = saved_add
                    modulegraph.replacePackage = saved_replace
            '''), locals(), globals())

    def test_addPackage(self):
        saved = modulegraph._packagePathMap
        self.assertIsInstance(saved, dict)
        try:
            modulegraph._packagePathMap = {}

            modulegraph.addPackagePath('foo', 'a')
            self.assertEqual(modulegraph._packagePathMap, { 'foo': ['a'] })

            modulegraph.addPackagePath('foo', 'b')
            self.assertEqual(modulegraph._packagePathMap, { 'foo': ['a', 'b'] })

            modulegraph.addPackagePath('bar', 'b')
            self.assertEqual(modulegraph._packagePathMap, { 'foo': ['a', 'b'], 'bar': ['b'] })

        finally:
            modulegraph._packagePathMap = saved


    def test_replacePackage(self):
        saved = modulegraph._replacePackageMap
        self.assertIsInstance(saved, dict)
        try:
            modulegraph._replacePackageMap = {}

            modulegraph.replacePackage("a", "b")
            self.assertEqual(modulegraph._replacePackageMap, {"a": "b"})
            modulegraph.replacePackage("a", "c")
            self.assertEqual(modulegraph._replacePackageMap, {"a": "c"})
            modulegraph.replacePackage("b", "c")
            self.assertEqual(modulegraph._replacePackageMap, {"a": "c", 'b': 'c'})

        finally:
            modulegraph._replacePackageMap = saved

class TestNode (unittest.TestCase):
    if not hasattr(unittest.TestCase, 'assertIsInstance'):
        def assertIsInstance(self, obj, types):
            self.assertTrue(isinstance(obj, types), '%r is not instance of %r'%(obj, types))
    def testBasicAttributes(self):
        n = modulegraph.Node("foobar.xyz")
        self.assertIsInstance(n.debug, int)
        self.assertEqual(n.identifier, n.graphident)
        self.assertEqual(n.identifier, 'foobar.xyz')
        self.assertEqual(n.filename, None)
        self.assertEqual(n.packagepath, None)
        self.assertEqual(n.code, None)
        self.assertEqual(n.globalnames, set())
        self.assertEqual(n.starimports, set())

    def testMapping(self):
        n = modulegraph.Node("foobar.xyz")
        self.assertEqual(n._namespace, {})

        self.assertFalse('foo' in n)
        self.assertRaises(KeyError, n.__getitem__, 'foo')
        self.assertEqual(n.get('foo'), None)
        self.assertEqual(n.get('foo', 'a'), 'a')
        n['foo'] = 42
        self.assertEqual(n['foo'], 42)
        self.assertTrue('foo' in n)
        self.assertEqual(n._namespace, {'foo':42})

    def testOrder(self):
        n1 = modulegraph.Node("n1")
        n2 = modulegraph.Node("n2")

        self.assertTrue(n1 < n2)
        self.assertFalse(n2 < n1)
        self.assertTrue(n1 <= n1)
        self.assertFalse(n1 == n2)
        self.assertTrue(n1 == n1)
        self.assertTrue(n1 != n2)
        self.assertFalse(n1 != n1)
        self.assertTrue(n2 > n1)
        self.assertFalse(n1 > n2)
        self.assertTrue(n1 >= n1)
        self.assertTrue(n2 >= n1)

    def testHashing(self):
        n1a = modulegraph.Node('n1')
        n1b = modulegraph.Node('n1')
        n2 = modulegraph.Node('n2')

        d = {}
        d[n1a] = 'n1'
        d[n2] = 'n2'
        self.assertEqual(d[n1b], 'n1')
        self.assertEqual(d[n2], 'n2')

    def test_infoTuple(self):
         n = modulegraph.Node('n1')
         self.assertEqual(n.infoTuple(), ('n1',))

    def assertNoMethods(self, klass):
        d = dict(klass.__dict__)
        del d['__doc__']
        del d['__module__']
        self.assertEqual(d, {})

    def assertHasExactMethods(self, klass, *methods):
        d = dict(klass.__dict__)
        del d['__doc__']
        del d['__module__']

        for nm in methods:
            self.assertTrue(nm in d, "%s doesn't have attribute %r"%(klass, nm))
            del d[nm]

        self.assertEqual(d, {})


    if not hasattr(unittest.TestCase, 'assertIsSubclass'):
        def assertIsSubclass(self, cls1, cls2, message=None):
            self.assertTrue(issubclass(cls1, cls2),
                    message or "%r is not a subclass of %r"%(cls1, cls2))

    def test_subclasses(self):
        self.assertIsSubclass(modulegraph.AliasNode, modulegraph.Node)
        self.assertIsSubclass(modulegraph.Script, modulegraph.Node)
        self.assertIsSubclass(modulegraph.BadModule, modulegraph.Node)
        self.assertIsSubclass(modulegraph.ExcludedModule, modulegraph.BadModule)
        self.assertIsSubclass(modulegraph.MissingModule, modulegraph.BadModule)
        self.assertIsSubclass(modulegraph.BaseModule, modulegraph.Node)
        self.assertIsSubclass(modulegraph.BuiltinModule, modulegraph.BaseModule)
        self.assertIsSubclass(modulegraph.SourceModule, modulegraph.BaseModule)
        self.assertIsSubclass(modulegraph.CompiledModule, modulegraph.BaseModule)
        self.assertIsSubclass(modulegraph.Package, modulegraph.BaseModule)
        self.assertIsSubclass(modulegraph.Extension, modulegraph.BaseModule)

        # These classes have no new functionality, check that no code
        # got added:
        self.assertNoMethods(modulegraph.BadModule)
        self.assertNoMethods(modulegraph.ExcludedModule)
        self.assertNoMethods(modulegraph.MissingModule)
        self.assertNoMethods(modulegraph.BuiltinModule)
        self.assertNoMethods(modulegraph.SourceModule)
        self.assertNoMethods(modulegraph.CompiledModule)
        self.assertNoMethods(modulegraph.Package)
        self.assertNoMethods(modulegraph.Extension)

        # AliasNode is basicly a clone of an existing node
        self.assertHasExactMethods(modulegraph.Script, '__init__', 'infoTuple')
        n1 = modulegraph.Node('n1')
        n1.packagepath = ['a', 'b']

        a1 = modulegraph.AliasNode('a1', n1)
        self.assertEqual(a1.graphident, 'a1')
        self.assertEqual(a1.identifier, 'n1')
        self.assertTrue(a1.packagepath is n1.packagepath)
        self.assertTrue(a1._namespace is n1._namespace)
        self.assertTrue(a1.globalnames is n1.globalnames)
        self.assertTrue(a1.starimports is n1.starimports)

        v = a1.infoTuple()
        self.assertEqual(v, ('a1', 'n1'))

        # Scripts have a filename
        self.assertHasExactMethods(modulegraph.Script, '__init__', 'infoTuple')
        s1 = modulegraph.Script('do_import')
        self.assertEqual(s1.graphident, 'do_import')
        self.assertEqual(s1.identifier, 'do_import')
        self.assertEqual(s1.filename, 'do_import')

        v = s1.infoTuple()
        self.assertEqual(v, ('do_import',))

        # BaseModule adds some attributes and a custom infotuple
        self.assertHasExactMethods(modulegraph.BaseModule, '__init__', 'infoTuple')
        m1 = modulegraph.BaseModule('foo')
        self.assertEqual(m1.graphident, 'foo')
        self.assertEqual(m1.identifier, 'foo')
        self.assertEqual(m1.filename, None)
        self.assertEqual(m1.packagepath, None)

        m1 = modulegraph.BaseModule('foo', 'bar',  ['a'])
        self.assertEqual(m1.graphident, 'foo')
        self.assertEqual(m1.identifier, 'foo')
        self.assertEqual(m1.filename, 'bar')
        self.assertEqual(m1.packagepath, ['a'])

class TestModuleGraph (unittest.TestCase):
    # Test for class modulegraph.modulegraph.ModuleGraph
    if not hasattr(unittest.TestCase, 'assertIsInstance'):
        def assertIsInstance(self, obj, types):
            self.assertTrue(isinstance(obj, types), '%r is not instance of %r'%(obj, types))

    def test_constructor(self):
        o = modulegraph.ModuleGraph()
        self.assertTrue(o.path is sys.path)
        self.assertEqual(o.lazynodes, {})
        self.assertEqual(o.replace_paths, ())
        self.assertEqual(o.debug, 0)

        # Stricter tests would be nice, but that requires
        # better control over what's on sys.path
        self.assertIsInstance(o.nspackages, dict)

        g = Graph.Graph()
        o = modulegraph.ModuleGraph(['a', 'b', 'c'], ['modA'], [
                ('fromA', 'toB'), ('fromC', 'toD')], 
                {
                    'modA': ['modB', 'modC'],
                    'modC': ['modE', 'modF'],
                }, g, 1)
        self.assertEqual(o.path, ['a', 'b', 'c'])
        self.assertEqual(o.lazynodes, {
            'modA': None,
            'modC': ['modE', 'modF'],
        })
        self.assertEqual(o.replace_paths, [('fromA', 'toB'), ('fromC', 'toD')])
        self.assertEqual(o.nspackages, {})
        self.assertTrue(o.graph is g)
        self.assertEqual(o.debug, 1)

    @expectedFailure
    def test_calc_setuptools_nspackages(self):
        self.fail("add tests")

    @expectedFailure
    def testImpliedReference(self):
        self.fail("implyNodeReference")

    @expectedFailure
    def test_findNode(self):
        self.fail("findNode")

    @expectedFailure
    def test_run_script(self):
        self.fail("run_script")

    @expectedFailure
    def test_import_hook(self):
        self.fail("import_hook")

    @expectedFailure
    def test_determine_parent(self):
        self.fail("determine_parent")

    @expectedFailure
    def test_find_head_package(self):
        self.fail("find_head_package")

    def test_load_tail(self):
        graph = modulegraph.ModuleGraph()

        record = []
        def import_module(partname, fqname, parent):
            record.append((partname, fqname, parent))
            if partname == 'raises':
                return None
            return modulegraph.Node(fqname)

        graph.import_module = import_module

        record = []
        root = modulegraph.Node('root')
        m = graph.load_tail(root, '')
        self.assertTrue(m is root)
        self.assertEqual(record, [
            ])

        record = []
        root = modulegraph.Node('root')
        m = graph.load_tail(root, 'sub')
        self.assertFalse(m is root)
        self.assertEqual(record, [
                ('sub', 'root.sub', root),
            ])

        record = []
        root = modulegraph.Node('root')
        m = graph.load_tail(root, 'sub.sub1')
        self.assertFalse(m is root)
        node = modulegraph.Node('root.sub')
        self.assertEqual(record, [
                ('sub', 'root.sub', root),
                ('sub1', 'root.sub.sub1', node),
            ])

        record = []
        root = modulegraph.Node('root')
        m = graph.load_tail(root, 'sub.sub1.sub2')
        self.assertFalse(m is root)
        node = modulegraph.Node('root.sub')
        node2 = modulegraph.Node('root.sub.sub1')
        self.assertEqual(record, [
                ('sub', 'root.sub', root),
                ('sub1', 'root.sub.sub1', node),
                ('sub2', 'root.sub.sub1.sub2', node2),
            ])
        
        self.assertRaises(ImportError, graph.load_tail, root, 'raises')
        self.assertRaises(ImportError, graph.load_tail, root, 'sub.raises')
        self.assertRaises(ImportError, graph.load_tail, root, 'sub.raises.sub')



    @expectedFailure
    def test_ensure_fromlist(self):
        self.fail("ensure_fromlist")

    @expectedFailure
    def test_find_all_submodules(self):
        self.fail("find_all_submodules")

    @expectedFailure
    def test_import_module(self):
        self.fail("import_module")

    @expectedFailure
    def test_load_module(self):
        self.fail("load_module")

    @expectedFailure
    def test_safe_import_hook(self):
        self.fail("safe_import_hook")

    @expectedFailure
    def test_scan_code(self):
        mod = modulegraph.Node('root')

        graph = modulegraph.ModuleGraph()
        code = compile('', '<test>', 'exec', 0, False)
        graph.scan_code(code, mod)
        self.assertEqual(list(graph.nodes()), [])

        graph = modulegraph.ModuleGraph()
        code = compile(textwrap.dedent('''\
            import sys
            import os.path
            
            def testfunc():
                import shutil
            '''), '<test>', 'exec', 0, False)
        graph.scan_code(code, mod)
        modules = [node.identifier for node in graph.nodes()]

        self.fail("tests needed....")


    @expectedFailure
    def test_load_package(self):
        self.fail("load_package")

    @expectedFailure
    def test_find_module(self):
        self.fail("find_module")

    @expectedFailure
    def test_create_xref(self):
        self.fail("create_xref")

    @expectedFailure
    def test_itergraphreport(self):
        self.fail("itergraphreport")

    def test_report(self):
        graph = modulegraph.ModuleGraph()

        saved_stdout = sys.stdout
        try:
            fp = sys.stdout = StringIO()
            graph.report()
            lines = fp.getvalue().splitlines()
            fp.close()

            self.assertEqual(len(lines), 3)
            self.assertEqual(lines[0], '')
            self.assertEqual(lines[1], 'Class           Name                      File')
            self.assertEqual(lines[2], '-----           ----                      ----')

            fp = sys.stdout = StringIO()
            graph._safe_import_hook('os', None, ())
            graph._safe_import_hook('sys', None, ())
            graph._safe_import_hook('nomod', None, ())
            graph.report()
            lines = fp.getvalue().splitlines()
            fp.close()

            self.assertEqual(lines[0], '')
            self.assertEqual(lines[1], 'Class           Name                      File')
            self.assertEqual(lines[2], '-----           ----                      ----')
            expected = []
            for n in graph.flatten():
                if n.filename:
                    expected.append([type(n).__name__, n.identifier, n.filename])
                else:
                    expected.append([type(n).__name__, n.identifier])
                    
            expected.sort()
            actual = [item.split() for item in lines[3:]]
            actual.sort()
            self.assertEqual(expected, actual)


        finally:
            sys.stdout = saved_stdout

    def test_graphreport(self):

        def my_iter(flatpackages="packages"):
            yield "line1\n"
            yield str(flatpackages) + "\n"
            yield "line2\n"

        graph = modulegraph.ModuleGraph()
        graph.itergraphreport = my_iter

        fp = StringIO()
        graph.graphreport(fp)
        self.assertEqual(fp.getvalue(), "line1\n()\nline2\n")

        fp = StringIO()
        graph.graphreport(fp, "deps")
        self.assertEqual(fp.getvalue(), "line1\ndeps\nline2\n")

        saved_stdout = sys.stdout
        try:
            sys.stdout = fp = StringIO()
            graph.graphreport()
            self.assertEqual(fp.getvalue(), "line1\n()\nline2\n")

        finally:
            sys.stdout = saved_stdout


    def test_replace_paths_in_code(self):
        graph = modulegraph.ModuleGraph(replace_paths=[
                ('path1', 'path2'),
                ('path3/path5', 'path4'),
            ])

        co = compile(textwrap.dedent("""
        [x for x in range(4)]
        """), "path4/index.py", 'exec', 0, 1)
        co = graph.replace_paths_in_code(co)
        self.assertEqual(co.co_filename, 'path4/index.py')

        co = compile(textwrap.dedent("""
        [x for x in range(4)]
        (x for x in range(4))
        """), "path1/index.py", 'exec', 0, 1)
        self.assertEqual(co.co_filename, 'path1/index.py')
        co = graph.replace_paths_in_code(co)
        self.assertEqual(co.co_filename, 'path2/index.py')
        for c in co.co_consts:
            if isinstance(c, type(co)):
                self.assertEqual(c.co_filename, 'path2/index.py')

        co = compile(textwrap.dedent("""
        [x for x in range(4)]
        """), "path3/path4/index.py", 'exec', 0, 1)
        co = graph.replace_paths_in_code(co)
        self.assertEqual(co.co_filename, 'path3/path4/index.py')

        co = compile(textwrap.dedent("""
        [x for x in range(4)]
        """), "path3/path5.py", 'exec', 0, 1)
        co = graph.replace_paths_in_code(co)
        self.assertEqual(co.co_filename, 'path3/path5.py')

        co = compile(textwrap.dedent("""
        [x for x in range(4)]
        """), "path3/path5/index.py", 'exec', 0, 1)
        co = graph.replace_paths_in_code(co)
        self.assertEqual(co.co_filename, 'path4/index.py')

    def test_createReference(self):
        graph = modulegraph.ModuleGraph()
        n1 = modulegraph.Node('n1')
        n2 = modulegraph.Node('n2')
        graph.addNode(n1)
        graph.addNode(n2)

        graph.createReference(n1, n2)
        outs, ins = map(list, graph.get_edges(n1))
        self.assertEqual(outs, [n2])
        self.assertEquals(ins, [])
        outs, ins = map(list, graph.get_edges(n2))
        self.assertEqual(outs, [])
        self.assertEquals(ins, [n1])

        e = graph.graph.edge_by_node('n1', 'n2')
        self.assertIsInstance(e, int)
        self.assertEqual(graph.graph.edge_data(e), 'direct')



if __name__ == "__main__":
    unittest.main()
