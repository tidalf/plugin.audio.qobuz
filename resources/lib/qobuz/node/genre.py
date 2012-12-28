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
import sys
import pprint

import xbmcgui, xbmc
import json

import qobuz
from constants import Mode
from flag import NodeFlag
from node import Node
from playlist import Node_playlist
from debug import info, warn, error
from gui.util import color

'''
    NODE FRIEND
'''
from track import Node_track

class Node_genre(Node):

    def __init__(self, parent = None, parameters = None, progress = None):
        super(Node_genre, self).__init__(parent, parameters)
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_GENRE
        self.set_label('Genre (i8n)')
        self.id = 1
        self.label2 = self.label
        self.url = None
        self.set_is_folder(True)
    
    def make_url(self,mode=Mode.VIEW):
        url = super(Node_genre, self).make_url(mode)
        if self.parent and self.parent.id: url+="&parent_id=" + self.parent.id
        return url
    
    def hook_post_data(self):
        self.id = self.get_property('id')
        self.label = self.get_property('name')
    
    def get_name(self):
        return self.get_property('name')
    
    def _build_down(self, xbmc_directory, lvl, flag = None):
        data = qobuz.registry.get(name='genre-list', id=self.id)
        if not data:
            warn(self, "No genre data")
            return False
        print pprint.pformat(data)
        for data in data['data']['genres']['items']:
            node = Node_genre()
            node.data = data
            self.add_child(node)
        return True
