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
import pprint

import xbmcgui, xbmc

import qobuz
from constants import Mode
from flag import NodeFlag
from node import Node
from debug import info, warn, error
from gui.util import color

'''
    NODE LABEL
'''


class Node_label(Node):

    def __init__(self, parent = None, parameters = None, progress = None):
        super(Node_label, self).__init__(parent, parameters)
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_LABEL
        self.set_label('Label (i8n)')
#        self.id = 1
        self.url = None
        self.set_is_folder(True)
    
    
    def hook_post_data(self):
        self.label = self.get_property('name')
        self.id = self.get_property('id')
        
    def _build_down(self, xbmc_directory, lvl, flag = None):
        data = qobuz.registry.get(name='label-list', id=self.id)
        if not data:
            warn(self, "No label data")
            return False
        print pprint.pformat(data)
        for data in data['data']['labels']['items']:
            node = Node_label()
            node.data = data
            self.add_child(node)
        return True
