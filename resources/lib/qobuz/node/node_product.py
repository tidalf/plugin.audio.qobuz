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
from debug import info
from tag.track import TagTrack
'''
    NODE PRODUCT
'''
from data.product import QobuzProduct
from tag.product import TagProduct
from node_track import node_track

class node_product(Node):
    
    def __init__(self, parent = None, params = None):
        super(node_product, self).__init__(parent)
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_PRODUCT
        self.set_content_type('songs')
    
    
    def _build_down(self, lvl, flag = None):
        o = QobuzProduct(self.id)
        data = o.get_data()
        pTag = TagProduct(data)
        self.set_label(pTag.getArtist() + ' - ' + pTag.getAlbum())
        if not data: return
        self.set_json(data)
        self.set_id(data['id'])
        for track in pTag.get_childs_with_type(TagTrack):#data['tracks']:
            c = node_track()
            c.set_id(track.id)
            c.set_label(track.getLabel())
            json_track = track.get_json()
            json_track['image'] = { 'large': data['image']['large'] }
            print "json_track: " + repr(json_track)
            c.set_json(json_track)
            c.set_url()
            self.add_child(c)

    def _get_xbmc_items(self, list, lvl, flag):
        for c in self.childs:
            tag = TagTrack(c.get_json())
            item = tag.getXbmcItem()
            url = c.get_url()
            item.setPath(url)
            self.attach_context_menu(item, NodeFlag.TYPE_PRODUCT)
            list.append((item.getProperty('path'), item, False))
        return True
        
    def _get_tag_items(self, list, lvl, flag):
        pass



