import unittest
import sys
import textwrap
import subprocess
import os
from modulegraph import modulegraph

class TestNativeImport (unittest.TestCase):
    # The tests check that Python's import statement
    # works as these tests expect.

    def importModule(self, name):
        if '.' in name:
            script = textwrap.dedent("""\
                try:
                    import %s
                except ImportError:
                    import %s
                print (%s.__name__)
            """) %(name, name.rsplit('.', 1)[0], name)
        else:
            script = textwrap.dedent("""\
                import %s
                print (%s.__name__)
            """) %(name, name)

        p = subprocess.Popen([sys.executable, '-c', script], 
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    'testpkg-import-from-init'),
        )
        data = p.communicate()[0]
        if sys.version_info[0] != 2:
            data = data.decode('UTF-8')
        data = data.strip()

        if data.endswith(' refs]'):
            # with --with-pydebug builds
            data = data.rsplit('\n', 1)[0].strip()

        sts = p.wait()

        if sts != 0:
            print (data)
        self.assertEqual(sts, 0)
        return data
        

    def testRootPkg(self):
        m = self.importModule('pkg')
        self.assertEqual(m, 'pkg')

    def testSubPackage(self):
        m = self.importModule('pkg.subpkg')
        self.assertEqual(m, 'pkg.subpkg')

    
class TestModuleGraphImport (unittest.TestCase):
    if not hasattr(unittest.TestCase, 'assertIsInstance'):
        def assertIsInstance(self, value, types):
            if not isinstance(value, types):
                self.fail("%r is not an instance of %r"%(value, types))

    def setUp(self):
        root = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'testpkg-import-from-init')
        self.mf = modulegraph.ModuleGraph(path=[ root ] + sys.path)
        #self.mf.debug = 999
        self.mf.run_script(os.path.join(root, 'script.py'))


    def testRootPkg(self):
        node = self.mf.findNode('pkg')
        self.assertIsInstance(node, modulegraph.Package)
        self.assertEqual(node.identifier, 'pkg')

    def testSubPackage(self):
        node = self.mf.findNode('pkg.subpkg')
        self.assertIsInstance(node, modulegraph.Package)
        self.assertEqual(node.identifier, 'pkg.subpkg')

        node = self.mf.findNode('pkg.subpkg.compat')
        self.assertIsInstance(node, modulegraph.SourceModule)
        self.assertEqual(node.identifier, 'pkg.subpkg.compat')

        node = self.mf.findNode('pkg.subpkg._collections')
        self.assertIsInstance(node, modulegraph.SourceModule)
        self.assertEqual(node.identifier, 'pkg.subpkg._collections')


if __name__ == "__main__":
    unittest.main()
