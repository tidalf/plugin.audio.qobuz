from os import path as P
import sys
import unittest

qobuzPath = P.abspath(P.join(P.dirname(__file__), P.pardir))
sys.path.append(qobuzPath)

class TestMain(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_import_qobuz(self):
        import qobuz
        self.assertIsNotNone(qobuz.base_path)
        self.assertIsNotNone(qobuz.data_path)
        return self
