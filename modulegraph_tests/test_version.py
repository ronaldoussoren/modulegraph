import os
import unittest

class TestVersions (unittest.TestCase):
    def test_package_version(self):
        import modulegraph

        fn = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'setup.cfg')
        with open(fn, 'rU') as fp:
            for ln in fp:
                if ln.startswith('version'):
                    version = ln.split('=')[-1].strip()
                    break
            else:
                self.fail("Cannot find setup version")

        self.assertEqual(version, modulegraph.__version__)

if __name__ == "__main__":
    unittest.main()

