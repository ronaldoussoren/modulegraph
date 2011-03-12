import unittest
from modulegraph import modulegraph

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

if __name__ == "__main__":
    unittest.main()
