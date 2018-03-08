from os import path as P
import sys
import unittest

qobuzPath = P.abspath(P.join(P.dirname(__file__), P.pardir))
sys.path.append(qobuzPath)

registry_data = {
}


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

    def test_module_constant(self):
        from qobuz.constants import Mode
        self.assertEqual(Mode.VIEW, 0x1)
        self.assertEqual(Mode.PLAY, 0x2)
        self.assertEqual(Mode.SCAN, 0x3)
        self.assertEqual(Mode.VIEW_BIG_DIR, 0x4)
        self.assertEqual(Mode.to_s(Mode.VIEW), 'view')
        self.assertEqual(Mode.to_s(Mode.PLAY), 'play')
        self.assertEqual(Mode.to_s(Mode.SCAN), 'scan')
        self.assertEqual(Mode.to_s(Mode.VIEW_BIG_DIR), 'view_big_dir')

    def test_module_debug(self):
        from qobuz.debug import getLogger
        logger = getLogger(__name__)
        self.assertIsNotNone(logger)

    def test_module_registry(self):
        from qobuz.registry import Registry
        import ConfigParser
        registry = Registry(None)
        self.assertIsNotNone(registry)
        self.assertEqual(registry.get('streamtype'), 'flac')
        self.assertRaises(ConfigParser.NoOptionError,
                          registry.get, 'UnknownKey')
