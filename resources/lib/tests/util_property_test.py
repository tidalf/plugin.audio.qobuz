import pytest
import unittest
import fixtures

data = fixtures.util_property_data


class TestUtilProperties(unittest.TestCase):
    def test_get(self):
        from qobuz.util import properties
        _path, value = properties.deep_get(data, 'foo')
        self.assertEqual(value, {'bar': 'baz'})
        _path, value = properties.deep_get(data, 'bar/baz/erf/long')
        self.assertEqual(value, 'FINALY')

    @classmethod
    def test_get_invalid_key(cls):
        from qobuz.util import properties
        with pytest.raises(KeyError):
            properties.deep_get(data, 'BADKEY')

    def test_string_converter(self):
        from qobuz.util import properties
        _path, value = properties.deep_get(data, 'foo', to=str)
        self.assertEqual(value, str({'bar': 'baz'}))

    def test_get_mapped(self):
        from qobuz.util import properties
        props = {
            'boom': {
                'to': properties.bool_converter,
                'default': False,
                'map': ['pof', 'pif', 'bar/baz/erf']
            }
        }
        _path, value = properties.get_mapped(data, props, 'boom')
        self.assertTrue(value)
