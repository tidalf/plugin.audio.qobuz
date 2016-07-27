'''
    qobuz.node
    ~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''

from qobuz.node.flag import Flag
from qobuz.debug import log


def getNode(qnt, params={}, data=None, **ka):
    '''Caching import ???
    '''
    nodeName = Flag.to_s(qnt)
    modulePath = nodeName
    moduleName = 'Node_' + nodeName
    Module = module_import(modulePath, moduleName)
    '''Initializing our new node
        - no parent
        - parameters
    '''
    parent = None
    if 'parent' in ka:
        parent = ka['parent']
    module = Module(parent, params)
    if data is not None:
        module.data = data
    return module


def mixin_factory(name, base, mixin):
    return type(name, (base, mixin), {})


def module_import(path, name, **ka):
    '''From node.foo import Node_foo
    '''
    modPackage = __import__(path, globals(), locals(), [name], -1)
    return getattr(modPackage, name)


class ErrorNoData(Exception):
    pass
