from qobuz.debug import getLogger

logger = getLogger('properties')

def is_number(value):
    try:
        float(value)
        return True
    except:
        return False

def identity_converter(value):
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

def deepGet(data, path, sep='/', to=identity_converter):
    parts = [p for p in path.split(sep) if p]
    if parts is None:
        return path, None
    root = data[parts.pop(0)]
    for _i, part in enumerate(parts):
        if part not in root:
            raise RuntimeError('InvalidSubPath<{}>'.format(part))
        root = root[part]
    return path, to(root)


def getMapped(data, props, key, sep='/', to=identity_converter):
    if key not in props:
        raise KeyError('No mapped key {}'.format(key))
    for path in props.get(key).map:
        try:
            _path, value = deepGet(data, path, sep=sep, to=to)
            return path, value
        except KeyError as e:
            logger.warning('error {}'.format(e))
    return path, None
