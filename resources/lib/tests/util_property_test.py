import pytest

import fixtures

data = {
    'baz': 'OK',
    'foo': {
        'bar': 'baz'
    },
    'pas': {
        'bras': {
            'pas': {
                'chocolat': 'true'
            }
        }
    },
    'bar': {
        'foo': 'PLOP',
        'baz': {
            'erf': {
                'long': 'FINALY'
            }
        }
    }
}


class TestUtilProperties(object):
    def test_get(self):
        from qobuz.util import properties
        _path, value = properties.deep_get(data, 'foo')
        assert value == {'bar': 'baz'}
        _path, value = properties.deep_get(data, 'bar/baz/erf/long')
        assert value == 'FINALY'

    def test_get_invalid_key(self):
        from qobuz.util import properties
        with pytest.raises(KeyError):
            properties.deep_get(data, 'BADKEY')

    def test_string_converter(self):
        from qobuz.util import properties
        _path, value = properties.deep_get(data, 'foo', to=str)
        assert value == str({'bar': 'baz'})

    def test_get_mapped(self):
        import json
        from qobuz.util import properties
        props = {
            'boom': {
                'to': properties.bool_converter,
                'default': False,
                'map': ['pof', 'pif', 'bar/baz/erf']
            }
        }
        _path, value = properties.get_mapped(data, props, 'boom')
        assert value == True
