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
import xbmcgui

import qobuz
from flag import NodeFlag as Flag
from inode import INode
from product import Node_product
from debug import warn, log
from gui.util import lang
from gui.util import getImage

'''
    @class Node_favorites:
'''
from track import Node_track


class Node_favorites(INode):

    def __init__(self, parent=None, parameters=None, progress=None):
        super(Node_favorites, self).__init__(parent, parameters)
        self.type = Flag.FAVORITES
        self.set_label(lang(30079))
        self.packby = ''
        self.name = lang(30079)
        self.label = lang(30079)
        self.content_type = 'songs'
        self.image = getImage('favorites')
        self.offset = self.get_parameter('offset') or 0
        
    def pre_build_down(self, Dir, lvl, whiteFlag, blackFlag):
        limit = qobuz.addon.getSetting('pagination_limit')
        data = qobuz.registry.get(
            name='user-favorites', limit=limit, offset=self.offset)
        if not data:
            warn(self, "Build-down: Cannot fetch favorites data")
            return False
        self.data = data['data']
        return True
    
    def _build_down(self, xbmc_directory, lvl, whiteFlag, blackFlag):
        for track in self.data['tracks']['items']:
            node = None
            node = Node_track()
            node.data = track
            self.add_child(node)
        for product in self.filter_products(self.data):
            self.add_child(product)
        return True

    def get_description(self):
        return self.get_property('description')

    def filter_products(self, data):
        list = []
        if not data:
            return list
        albumseen = {}
        for track in data['albums']['items']:
            # warn(self, 'Track ' + track)
            json = track
            json[u'interpreter'] = track['artist']['name']
            product = Node_product()
            product.data = json
            id = product.id
            if id in albumseen:
                continue
            albumseen[id] = 1
            list.append(product)
        return list

    def add(self):
        #HEavily bugged
            from gui.directory import Directory
            from renderer.xbmc import QobuzXbmcRenderer as renderer
            nt = None
            try:
                nt = int(self.get_parameter('nt'))
            except:
                warn(self, "No node type...abort")
                return False
            id = None
            try:
                id = self.get_parameter('nid')
            except:
                pass
            depth = -1
            try:
                depth = int(self.get_parameter('depth'))
            except:
                pass
            view_filter = 0
            try:
                view_filter = int(self.get_parameter('view-filter'))
            except:
                pass
            render = renderer(nt, id)
            render.set_depth(depth)
            render.set_filter(view_filter)
            render.set_root_node()
            Dir = Directory(render.root, qobuz.boot.handle, True)
            flags = Flag.TRACK | Flag.STOPBUILD
            if render.root.type & Flag.TRACK:
                flags = Flag.TRACK
            ret = render.root.build_down(Dir, depth, flags, )
            if not ret:
                Dir.end_of_directory()
                return False
            trackids = []
            if len(Dir.nodes) < 1:
                warn(self, "No track to add to favorites")
                Dir.end_of_directory()
                return False
            for node in Dir.nodes:
                trackids.append(str(node.id))
            strtracks = ','.join(trackids)
            ret = qobuz.api.favorite_create(track_ids=strtracks)
            qobuz.registry.delete(name='user-favorites')
            Dir.end_of_directory()
            return True

    def remove(self):
        log(self, "Removing favorite: " + repr(self.id))
        if not qobuz.api.favorite_delete(track_ids=str(self.id)):
            return False
        qobuz.registry.delete(name='user-favorites')
        return True
