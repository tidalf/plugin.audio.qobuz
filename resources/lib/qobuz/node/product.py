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
from debug import info, warn, error
'''
    NODE PRODUCT
'''
from cache.product import Cache_product

from track import Node_track

class Node_product(Node):

    def __init__(self, parent = None, params = None):
        super(Node_product, self).__init__(parent, params)
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_PRODUCT
        self.set_content_type('songs')
        self.cache = None


    def _set_cache(self):
        id = self.get_id()
        if not id:
            try: id = self.get_parameter('nid')
            except: pass
        if not id:
            error(self, "Cannot set product cache without id")
            return False
        self.cache = Cache_product(id)
        self.set_id(id)
        return True
    
    def _build_down(self, xbmc_directory, lvl, flag = None, progress = None):
        if not self._set_cache():
            error(self, "Cannot set product cache")
            return False
        data = self.cache.fetch_data()
        if not data:
            warn(self, "Cannot fetch product data")
            return False
        self.set_data(data)     
        for track in data['tracks']:
            node = Node_track()
            node.set_data(track)
            self.add_child(node)

    
    def make_XbmcListItem(self):
        import xbmcgui
        item = xbmcgui.ListItem(
                                self.get_label(),
                                self.get_label2(),
                                self.get_image(),
                                self.get_image(),
                                self.make_url(),                         
                                )
        item.setInfo('music', infoLabels = {
                                            'genre': self.get_genre(),
                                            'year': self.get_year()
                                            })
        self.attach_context_menu(item)
        return item

    ''' 
    PROPERTIES 
    '''
    def get_artist(self):
        a = self.get_property(('artist', 'name'))
        if a: return a
        a = self.get_property(('interpreter', 'name'))
        if a: return a
        a = self.get_property(('composer', 'name'))
        return a
    
    def get_artist_id(self):
        a = self.get_property(('artist', 'id'))
        if a: return a
        a = self.get_property(('interpreter', 'id'))
        if a: return a
        a = self.get_property(('composer', 'id'))
        return a
    
    def get_title(self):
        title =  self.get_property('title')
        if not title: title = self.get_property('subtitle')
        return title
    
    def get_image(self):
        image = self.get_property(('image', 'large'))
        image = image.replace('_230.', '_600.')
        if image: 
            self.image = image
            return image
        if self.parent: 
            image =  self.parent.get_image()
            if image: self.image = image
        return self.image
    
    def get_label(self):
        label = ''.join((self.get_artist(), ' - ', self.get_title()))
        return label
    
    def get_label2(self):
        return self.get_label()
    
    def get_genre(self):
        return self.get_property(('genre', 'name'))
    
    
    def get_year(self):
        date = self.get_property('release_date')
        year = 0
        try: year = int(date.split('-')[0])
        except: pass
        return year
    
    def get_description(self):
        return self.get_property('description')
    
    