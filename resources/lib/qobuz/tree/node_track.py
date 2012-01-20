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

import qobuz
from constants import *
from flag import NodeFlag
from node import node
'''
    NODE TRACK
'''
from data.track import QobuzTrack
from utils.tag import QobuzTagTrack
class node_track(node):
    
    def __init__(self, parent = None):
        super(node_track, self).__init__(parent)
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_TRACK
        
    def _build_down(self, lvl, flag = None):
        self.setLabel("Track ID[" + self.getId() + "] " + self.getLabel())
        if not (flag & NodeFlag.DONTFETCHTRACK):
            o = QobuzTrack(self.id)
            self.setJson(o.get_data())
    
    def get_xbmc_item(self, list):
        t = QobuzTagTrack(self.getJson())
        self.setUrl()
        list.append((self.url, t.getXbmcItem(), True))
        for c in self.childs:
            c.get_xbmc_item(list)