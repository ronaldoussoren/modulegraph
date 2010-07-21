import unittest

import os, shutil

from modulegraph import modulegraph

class OsListDirTestCase(unittest.TestCase):
    tmp_dir = "test.tmp"
    def setUp(self):
        os.mkdir(self.tmp_dir)
    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def testListDir(self):
        # current directory exists
        self.assertTrue(len(modulegraph.os_listdir(".")) >= 0)
        # maybe use os.tmpnam, but that gives a runtime warning.
        self.assertRaises(OSError,
                modulegraph.os_listdir, "hopefully/not/existing/dir")
        self.assertRaises(OSError,
                modulegraph.os_listdir, "hopefully-not-existing-dir")

        # defect zip file: raises IOError no such file ...
        fn = self.tmp_dir + "/empty.zip"
        open(fn, "w")
        self.assertRaises((IOError, OSError),
                modulegraph.os_listdir, fn)

class DummyModule(object):
    packagepath = None
    def __init__(self, ppath):
        self.packagepath = ppath

class FindAllSubmodulesTestCase(unittest.TestCase):
    def testNone(self):
        mg = modulegraph.ModuleGraph()
        # empty packagepath
        m = DummyModule(None)
        sub_ms = []
        for sm in mg.find_all_submodules(m):
            sub_ms.append(sm)
        self.assertEqual(sub_ms, [])

    def testSimple(self):
        mg = modulegraph.ModuleGraph()
        # a string does not break anything although it is split into its characters
        # BUG: "/hi/there" will read "/"
        m = DummyModule("xyz")
        sub_ms = []
        for sm in mg.find_all_submodules(m):
            sub_ms.append(sm)
        self.assertEqual(sub_ms, [])

    def testSlashes(self):
        # a string does not break anything although it is split into its characters
        # BUG: "/xyz" will read "/" so this one already triggers missing itertools
        mg = modulegraph.ModuleGraph()
        m = DummyModule("/xyz")
        sub_ms = []
        for sm in mg.find_all_submodules(m):
            sub_ms.append(sm)
        self.assertEqual(sub_ms, [])

if __name__ == '__main__':
    unittest.main()
