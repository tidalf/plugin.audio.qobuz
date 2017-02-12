'''
    qobuz.node
    ~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''

from qobuz.node.flag import Flag


def getNode(qnt, parameters={}, data=None, parent=None, **ka):
    return module_import(Flag.to_s(qnt))(parent=parent,
                                         parameters=parameters,
                                         data=data,
                                         **ka)


def mixin_factory(name, base, mixin):
    return type(name, (base, mixin), {})


__cache__ = {}


def module_import(path):
    '''From node.foo import Node_foo
    '''
    name = 'Node_%s' % path
    if name not in __cache__:
        __cache__[name] = getattr(
            __import__(path, globals(), locals(), [name], -1), name)
    return __cache__[name]


class ErrorNoData(Exception):
    pass
