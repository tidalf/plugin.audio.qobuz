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
from node import Node
'''
    NODE TRACK
'''
from cache.track import Cache_track
from tag.track import TagTrack

class Node_track(Node):
    
    def __init__(self, parent = None, parameters = None):
        super(Node_track, self).__init__(parent, parameters)
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_TRACK
        self.set_content_type('songs')
        
    def _build_down(self, lvl, flag = None):
        if flag & NodeFlag.DONTFETCHTRACK:
            #print "Don't fetch track data"
            return False
        o = QobuzTrack(self.id)
        data = o.get_data()
        self.set_json(data)
        self.set_id(data['id'])
        
    def _get_xbmc_items(self, list, lvl, flag):
        t = TagTrack(self.get_json())
        self.set_url()
        item =  t.getXbmcItem(context = 'album', pos = 0, fanArt = 'fanArt')
        self.attach_context_menu(item, NodeFlag.TYPE_TRACK)
        list.append((item.getProperty('path'),item , False))
        return True
        
    def _get_tag_items(self, list, lvl, flag):
        #print "Get track data!"
        data = self.get_json()
        if not data: return False
        list.append(data)
        