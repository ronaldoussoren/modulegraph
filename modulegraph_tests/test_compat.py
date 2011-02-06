import sys
import unittest
import modulegraph._compat as compat

try:
    bytes
except NameError:
    bytes = str

class CompatTests (unittest.TestCase):
    def test_B(self):
        v = compat.B("hello")
        self.assertTrue(isinstance(v, bytes))

    def test_Bchr(self):
        v = compat.Bchr(ord('A'))
        if sys.version_info[0] == 2: 
            self.assertTrue(isinstance(v, bytes))
            self.assertEqual(v, compat.B('A'))
        else:
            self.assertTrue(isinstance(v, int))
            self.assertEqual(v, ord('A'))

if __name__ == "__main__":
    unittest.main()
