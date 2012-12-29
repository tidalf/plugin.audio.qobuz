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

import xbmcgui

import qobuz
from constants import Mode
from flag import NodeFlag
from node import Node
from product import Node_product
from debug import info, warn, error
from gui.util import lang
from gui.util import color

'''
    NODE PLAYLIST
'''
from track import Node_track

class Node_favorites(Node):

    def __init__(self, parent = None, parameters = None, progress = None):
        super(Node_favorites, self).__init__(parent, parameters)
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_FAVORITES
        self.set_label(lang(30079))
        self.packby = ''  
        self.name = lang(30079)
        self.label = lang(30079)    
        self.content_type = 'songs'

    def _build_down(self, xbmc_directory, lvl, flag = None):
        offset = self.get_parameter('offset') or 0
        limit = qobuz.addon.getSetting('pagination_limit')
        data = qobuz.registry.get(name='user-favorites', limit=limit, offset=offset)
        print pprint.pformat(data)
        if not data:
            warn(self, "Build-down: Cannot fetch favorites data")
            return False
        self.data = data
        for track in data['data']['tracks']['items']:
            node = None
            node = Node_track()
            node.data = track
            self.add_child(node)
        for product in self.filter_products(data):
            self.add_child(product)
        self.add_pagination(data['data'])
        return True
        
#    def get_name(self):
#        name = self.get_property('name')
#        return name
#    
#    def get_owner(self):
#        return self.get_property(('owner', 'name'))
#            
    def get_description(self):
        return self.get_property('description')
    
    def filter_products(self, data):
        list = []
        if not data: return list
        albumseen = {}
        for track in data['data']['albums']['items']:
            #warn(self, 'Track ' + track)
            json = track
            json[u'interpreter'] = track['artist']['name']
            product = Node_product()
            product.data = json 
            id = product.id
            if id in albumseen: continue
            albumseen[id] = 1
            list.append(product)
        return list

    def add(self):
            from gui.directory import Directory
            from renderer.xbmc import Xbmc_renderer as renderer
            nt = None
            try: nt = int(self.get_parameter('nt'))
            except:
                warn(self, "No node type...abort")
                return False
            id = None
            try: id = self.get_parameter('nid')        
            except: pass 
            depth = -1
            try: depth = int(self.get_parameter('depth'))
            except: pass
            view_filter = 0
            try: view_filter = int(self.get_parameter('view-filter'))
            except: pass
            render = renderer(nt, id)
            render.set_depth(depth)
            render.set_filter(view_filter)
            render.set_root_node()
            dir = Directory(render.root, qobuz.boot.handle, True)
            flags = NodeFlag.TYPE_TRACK | NodeFlag.DONTFETCHTRACK
            if render.root.type & NodeFlag.TYPE_TRACK:
                flags = NodeFlag.TYPE_TRACK
            ret = render.root.build_down(dir, depth, flags)
            if not ret: 
                dir.end_of_directory()
                return False
            trackids = []
            if len(dir.nodes) < 1:
                warn(self, "No track to add to favorites")
                dir.end_of_directory()
                return False
            for node in dir.nodes:
                trackids.append(str(node.id))
            strtracks = ','.join(trackids)
            ret = qobuz.api.favorite_create(track_ids=strtracks)
            qobuz.registry.delete(name='user-favorites')
            dir.end_of_directory()
            return True
    
    def remove(self):
        print "Removing favorite"
        if not qobuz.api.favorite_delete(track_ids=str(self.id)):
            return False
        qobuz.registry.delete(name='user-favorites')
        return True
