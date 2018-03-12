
'''
    qobuz.util.properties
    ~~~~~~~~~~~~~~~~~~~~~

    :part_of: kodi-qobuz
    :copyright: (c) 2012-2018 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.debug import getLogger

logger = getLogger('properties')


def is_number(value):
    try:
        float(value)
        return True
    except Exception as _:
        return False


def identity_converter(value):
    return value


def unicode_converter(value):
    try:
        return value.decode('ascii', errors='replace')
    except Exception as e:
        logger.info('error decoding %r utf: %s', value, e)
    return value


def bool_converter(value):
    if value in [True, False]:
        return value
    if isinstance(value, basestring):
        if value.lower() in ['yes', 'true']:
            return True
        return False
    if is_number(value):
        if value == 0:
            return False
        return True
    if value:
        return True
    return False


def deep_get(data, path, sep='/', to=identity_converter):
    parts = [p for p in path.split(sep) if p]
    if parts is None:
        return path, None
    root = data[parts.pop(0)]
    if root is None:
        return path, None
    for _i, part in enumerate(parts):
        if part not in root:
            raise KeyError(part)
        root = root[part]
    return path, to(root)


def get_mapped(data, props, key, sep='/', default=None):
    if key not in props:
        raise KeyError('No mapped key {}'.format(key))
    prop = props.get(key)
    if 'alias' in prop:
        alias = prop.get('alias')
        if alias not in props:
            raise KeyError('No mapped alias key {}'.format(alias))
        prop = props.get(alias)
    to = prop.get('to') if 'to' in prop else identity_converter
    for path in prop.get('map'):
        try:
            _path, value = deep_get(data, path, sep=sep, to=to)
            return path, value
        except KeyError:
            pass
    return path, default
