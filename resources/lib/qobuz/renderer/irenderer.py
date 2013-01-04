#     Copyright 2011 Joachim Basmaison, Cyril Leclerc
#
#     This file is part of xbmc-qobuz.
#
#     xbmc-qobuz is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     xbmc-qobuz is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.   See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with xbmc-qobuz.   If not, see <http://www.gnu.org/licenses/>.
import qobuz
from debug import log
from exception import QobuzXbmcError
from node.flag import NodeFlag as Flag

import pprint

class IRenderer(object):

    def __init__(self, node_type, node_id=None):
        self.node_type = node_type
        self.node_id = node_id
        self.root = None
        self.blackFlag = 0 | Flag.STOPBUILD
        self.depth = 1
        self.asList = False
        self.nodes = []

    def to_s(self):
        return pprint.pformat(self)

    def import_node(self, nt, params):
        """ Converting int flag to string """
        nodeName = Flag.to_s(nt)
        modulePath = 'node.' + nodeName
        moduleName = 'Node_' + nodeName
        """ from node.foo import Node_foo """
        try:
            Module = __import__(modulePath, globals(), 
                                locals(), [moduleName], -1)
        except Exception as e:
            error = {
                     'modulePath': modulePath,
                     'moduleName': moduleName,
                     'nodeName': nodeName,
                     'nodeType': nt,
                     'error': e
            }
            raise QobuzXbmcError(who=self, 
                                 what="module_loading_error", 
                                 additional=pprint.pformat(error))
        """ Getting Module from Package """
        node = getattr(Module, moduleName)
        """ Passing default parameter to our node (?a=2&b=3..) """
        root = node(None, params)
        log(self, "Returning node: " + repr(root))
        return root
    
    """
        We are setting our root node based on nt parameter
        
    """
    def set_root_node(self):
        if self.root: return False
        root = self.import_node(self.node_type, qobuz.boot.params)
        self.root = root
        return True
