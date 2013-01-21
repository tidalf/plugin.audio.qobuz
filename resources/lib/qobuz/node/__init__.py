'''
    qobuz.node
    ~~~~~~~~~~
    
    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''

__all__ = ['getNode', 'flag']

from node.flag import Flag
from debug import log

def getNode(qnt, params = {}):
        ''' Caching import ??? '''
        nodeName = Flag.to_s(qnt)
        modulePath = nodeName
        moduleName = 'Node_' + nodeName
        """ from node.foo import Node_foo """
        modPackage = __import__(modulePath, globals(), 
                                locals(), [moduleName], -1)
        """ Getting Module from Package """
        nodeModule = getattr(modPackage, moduleName)
        """ 
            Initializing our new node 
            - no parent 
            - parameters 
            """
        parent = None
        if 'parent' in params:
            parent = params['parent']
            del params['parent']
        node = nodeModule(parent, params)
        return node