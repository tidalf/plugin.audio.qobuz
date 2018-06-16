
'''
    qobuz.util.properties
    ~~~~~~~~~~~~~~~~~~~~~

    :part_of: kodi-qobuz
    :copyright: (c) 2012-2018 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.debug import getLogger
from qobuz.util.converter import strip_tags

logger = getLogger('properties')
SEPARATOR = '/'


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


def strip_html_converter(value):
    return strip_tags(value)


def split_path(path, separator):
    return [p for p in path.split(separator) if p]


def _deep_get_routine(root, parts):
    for _i, part in enumerate(parts):
        if part not in root:
            raise KeyError(part)
        root = root[part]
    return root


def deep_get(data, path, to=identity_converter, default=None):
    parts = split_path(path, SEPARATOR)
    if parts is None:
        return path, None
    root = data[parts.pop(0)]
    if root is None:
        return path, None
    root = _deep_get_routine(root, parts)
    if root is None:
        root = path, default
    return path, to(root)


def get_mapped(data, props, key, default=None):
    if key not in props:
        raise KeyError('No mapped key {}'.format(key))
    if data is None:
        logger.info('noData %s: %s', key, default)
        return None, default
    prop = props.get(key)
    if 'alias' in prop:
        alias = prop.get('alias')
        if alias not in props:
            raise KeyError('No mapped alias key {}'.format(alias))
        prop = props.get(alias)
    converter = prop.get('to') if 'to' in prop else identity_converter
    for path in prop.get('map'):
        try:
            _path, value = deep_get(data, path, to=converter, default=default)
            return path, value
        except KeyError:
            pass
    return None, default
