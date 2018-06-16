from HTMLParser import HTMLParser
import math
import urllib

from qobuz.util import common


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    if html is None:
        return None
    stripper = MLStripper()
    stripper.feed(html)
    return stripper.get_data()


class Converter(object):

    @classmethod
    def raw(cls, data, default=None):
        return data

    @classmethod
    def string(cls, data, default=None):
        if common.is_empty(data):
            return default
        return str(data)

    @classmethod
    def int(cls, data, default=None):
        if common.is_empty(data):
            return default
        return int(data)

    @classmethod
    def float(cls, data, default=None):
        if common.is_empty(data):
            return default
        return float(data)

    @classmethod
    def bool(cls, data, default=None):
        return common.input2bool(data)

    @classmethod
    def bool2str(cls, data, default='false'):
        if data is None:
            return default
        return str(bool(data)).lower()

    @classmethod
    def unquote(cls, data, default=None):
        if common.is_empty(data):
            return default
        return urllib.unquote_plus(data)

    @classmethod
    def quote(cls, data, default=None):
        if common.is_empty(data):
            return default
        return urllib.quote_plus(data)

    @classmethod
    def math_floor(cls, data, default=None):
        if common.is_empty(data):
            return default
        return math.floor(data)

    @classmethod
    def strip_html(cls, data, default=None):
        if common.is_empty(data):
            return default
        return strip_tags(data)

    @classmethod
    def color(cls, data, default=None):
        if common.is_empty(data):
            return default
        if data.startswith('#') and len(data) == 7:
            return '%sFF' % data
        return data


converter = Converter()
