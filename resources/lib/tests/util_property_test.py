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
        _path, value = properties.deepGet(data, 'foo')
        assert value == {'bar': 'baz'}
        _path, value = properties.deepGet(data, 'bar/baz/erf/long')
        assert value == 'FINALY'

    def test_get_invalid_key(self):
        from qobuz.util import properties
        with pytest.raises(KeyError):
            properties.deepGet(data, 'BADKEY')

    def test_string_converter(self):
        from qobuz.util import properties
        _path, value = properties.deepGet(data, 'foo', to=str)
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
        _path, value = properties.getMapped(data, props, 'boom', to=str)
        assert value == str({'long': 'FINALY'})
        _path, value = properties.getMapped(data, props, 'boom', to=json.dumps)
        assert value == '{"long": "FINALY"}'
        _path, value = properties.getMapped(
            data, props, 'boom', to=properties.bool_converter)
        assert value == True
