import sys
from os import path as P

qobuzPath = P.abspath(P.join(P.dirname(__file__), P.pardir))
sys.path.append(qobuzPath)

class TestMain(object):
    def test_import_qobuz(self):
        import qobuz
        assert qobuz.base_path
        assert qobuz.data_path
        return self