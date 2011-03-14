import unittest
from modulegraph import modulegraph
import pkg_resources
import os

try:
    bytes
except NameError:
    bytes = str

try:
    expectedFailure = unittest.expectedFailure
except AttributeError:
    expectedFailure = lambda function: function

class TestModuleGraph (unittest.TestCase):
    @expectedFailure
    def testMissing(self):
        self.fail("add tests")


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

        self.assertEqual(modulegraph._os_listdir('/etc/'), os.listdir('/etc'))
        self.assertRaises(OSError, modulegraph._os_listdir, '/etc/hosts/foobar')
        self.assertRaises(OSError, modulegraph._os_listdir, os.path.join(root, 'test.egg', 'bar'))

        self.assertEqual(list(sorted(modulegraph._os_listdir(os.path.join(root, 'test.egg', 'foo')))),
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

    @expectedFailure
    def test_moduleInfoForPath(self):
        self.fail("Missing test for modulegraph.moduleInfoForPath")





if __name__ == "__main__":
    unittest.main()
