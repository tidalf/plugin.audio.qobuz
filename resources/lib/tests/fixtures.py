import sys
from os import path as P

qobuzPath = P.abspath(P.join(P.dirname(__file__), P.pardir))
sys.path.append(qobuzPath)

util_property_data = {
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