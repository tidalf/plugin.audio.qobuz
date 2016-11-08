'''
    qobuz.util.common
    ~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2015 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''

def is_number(value):
    try:
        float(value)
    except ValueError:
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
