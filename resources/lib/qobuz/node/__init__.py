'''
    qobuz.node
    ~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''

from qobuz.node.flag import Flag
from qobuz.debug import log


def getNode(qnt, params={}, data=None, parent=None, **ka):
    nodeName = Flag.to_s(qnt)
    moduleName = 'Node_' + nodeName
    Module = module_import(nodeName, moduleName)
    return Module(parent, params, data=data)


def mixin_factory(name, base, mixin):
    return type(name, (base, mixin), {})


def module_import(path, name, **ka):
    '''From node.foo import Node_foo
    '''
    modPackage = __import__(path, globals(), locals(), [name], -1)
    return getattr(modPackage, name)


class ErrorNoData(Exception):
    pass
