from qobuz.util import data as dataUtil
from qobuz.util import common
import urllib

class Converter(object):

    def raw(self, data, default=None):
        return data

    def string(self, data, default=None):
        if data is None:
            return default
        return str(data)

    def int(self, data, default=None):
        if common.is_empty(data):
            return default
        return int(data)

    def float(self, data, default=None):
        if common.is_empty(data):
            return default
        return float(data)
    def bool(self, data, default=None):
        return common.input2bool(data)

    def unquote(self, data, default=None):
        if data is None:
            return default
        return urllib.unquote_plus(data)

    def quote(self, data, default=None):
        if data is None:
            return default
        return urllib.quote_plus(data)

    def math_floor(self, data, default=None):
        if data is None:
            return default
        return floor(data)

    def htm2xbmc(self, data, default=None):
        if data is None:
            return default
        return common.htm2xbmc(data)

    def color(self, data, default=None):
        if data is None:
            return default
        if data.startswith('#') and len(data) == 7:
            return '%sFF' % data
        return data

converter = Converter()
