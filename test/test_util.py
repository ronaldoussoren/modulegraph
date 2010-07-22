import unittest
import encodings
import encodings.aliases
from modulegraph import util

class TestUtil (unittest.TestCase):
    def test_imp_find_module(self):
        fn = util.imp_find_module('encodings.aliases')[1]
        assert encodings.aliases.__file__.startswith(fn)

    def test_imp_walk(self):
        imps = list(util.imp_walk('encodings.aliases'))
        assert len(imps) == 2

        assert imps[0][0] == 'encodings'
        assert encodings.__file__.startswith(imps[0][1][1])

        assert imps[1][0] == 'aliases'
        assert encodings.aliases.__file__.startswith(imps[1][1][1])

if __name__ == "__main__":
    unittest.main()
