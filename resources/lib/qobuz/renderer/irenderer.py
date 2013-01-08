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
from gui.util import containerRefresh

import pprint

class IRenderer(object):

    def __init__(self, node_type, parameters=None):
        self.node_type = node_type
        self.parameters = parameters
        self.root = None
        self.whiteFlag = Flag.ALL
        self.blackFlag = Flag.STOPBUILD
        self.depth = 1
        self.asList = False
        self.nodes = []

    def to_s(self):
        return pprint.pformat(self)

    def import_node(self, nt, params):
        """ Converting int flag to string """
        nodeName = Flag.to_s(nt)
        #print "Loading module: " + nodeName
        modulePath = 'node.' + nodeName
        moduleName = 'Node_' + nodeName
        #print "Info %s / %s" % (modulePath, moduleName)
        """ from node.foo import Node_foo """
#        try:
        modPackage = __import__(modulePath, globals(), 
                                locals(), [moduleName], -1)
#        except Exception as e:
#            error = {
#                     'modulePath': modulePath,
#                     'moduleName': moduleName,
#                     'nodeName': nodeName,
#                     'nodeType': nt,
#                     'error': e
#            }
#            raise QobuzXbmcError(who=self, 
#                                 what="module_loading_error", 
#                                 additional=pprint.pformat(error))
        """ Getting Module from Package """
        nodeModule = getattr(modPackage, moduleName)
        """ 
            Initializing our new node 
            - no parent 
            - parameters 
            """
        node = nodeModule(None, params)
        #log(self, "Returning node: " + repr(node))
        return node
    
    """
        We are setting our root node based on nt parameter
        
    """
    def set_root_node(self):
        if self.root: return self.root
        self.root = self.import_node(self.node_type, self.parameters)
        return self.root
    
    def has_method_parameter(self):
        if 'nm' in self.parameters:
            return True
        return False
    
    def execute_method_parameter(self):
        if 'nm' in self.parameters:
            methodName = self.parameters['nm']
            del self.parameters['nm']
            log(self, "Executing method on node: " + repr(methodName))
            if getattr(self.root, methodName)():
                return True
            return False