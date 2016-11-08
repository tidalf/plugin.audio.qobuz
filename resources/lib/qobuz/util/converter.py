import urllib
from HTMLParser import HTMLParser
import math

from qobuz.util import data as dataUtil
from qobuz.util import common
from qobuz import debug

class MLStripper(HTMLParser):

    def __init__(self):
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

class Converter(object):

    def raw(self, data, default=None):
        return data

    def string(self, data, default=None):
        if common.is_empty(data):
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
        if common.is_empty(data):
            return default
        return urllib.unquote_plus(data)

    def quote(self, data, default=None):
        if common.is_empty(data):
            return default
        return urllib.quote_plus(data)

    def math_floor(self, data, default=None):
        if common.is_empty(data):
            return default
        return math.floor(data)

    def strip_html(self, data, default=None):
        if common.is_empty(data):
            return default
        return strip_tags(data)

    def color(self, data, default=None):
        if common.is_empty(data):
            return default
        if data.startswith('#') and len(data) == 7:
            return '%sFF' % data
        return data

converter = Converter()
