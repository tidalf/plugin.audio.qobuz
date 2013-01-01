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
from node.flag import NodeFlag
#from debug import info, warn, error, debug
import pprint

class IRenderer(object):

    def __init__(self, node_type, node_id = None):
        self.node_type = node_type
        self.node_id = node_id
        self.root = None
        self.filter = NodeFlag.NODE
        self.depth = 1

    def to_s(self):
        return pprint.pformat(self)

    def set_depth(self, d):
        self.depth = d

    def set_filter(self, filter):
        self.filter = filter

    def set_root_node(self):
        import sys
        root = None
        nodeName = NodeFlag.to_s(self.node_type)
        modulePath = 'node.' + nodeName
        moduleName = 'Node_' + nodeName
        Module =__import__(modulePath, globals(), locals(), [moduleName], -1)
        node = getattr(Module, moduleName)
        root = node(None, qobuz.boot.params)
        root.id = self.node_id
        self.root = root
        return True
