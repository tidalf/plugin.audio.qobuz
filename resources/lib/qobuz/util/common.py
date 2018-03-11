'''
    qobuz.util.common
    ~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2015 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import json
import functools
from qobuz import config
from qobuz import constants


def is_number(value):
    try:
        float(value)
    except Exception as _:
        return False
    return True


def input2bool(value):
    if value in [False, True]:
        return value
    elif is_number(value):
        if value == 0:
            return False
        return True
    elif isinstance(value, basestring):
        value = value.lower()
        if value in ['false', '0']:
            return False
        return True


def is_empty(value):
    if value is None or value == '':
        return True
    return False


separators = (',', ':')
json_dumps = functools.partial(json.dumps, separators=separators)
json_dump = functools.partial(json.dump, separators=separators)


class Struct(object):
    def __init__(self, **entries):
        self.__dict__.update(entries)

    def __iter__(self):
        for key, value in self.__dict__.items():
            yield key, value


def get_default_image_size():
    text_size = config.app.registry.get('image_default_size', default='small')
    return constants.TEXT_IMAGE_TO_SIZE[text_size]
