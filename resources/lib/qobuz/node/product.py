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

import xbmcgui

import qobuz
from constants import *
from flag import NodeFlag
from node import Node
from debug import info, warn, error
'''
    NODE PRODUCT
'''
from cache.product import Cache_product
from cache.purchases import Cache_purchases


from track import Node_track

SPECIAL_PURCHASES = ['0000020110926', '0000201011300', '0000020120220', '0000020120221']

class Node_product(Node):

    def __init__(self, parent = None, params = None):
        super(Node_product, self).__init__(parent, params)
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_PRODUCT
        self.set_content_type('songs')
        self.cache = None
        self.is_special_purchase = False

    def set_cache(self):
        id = self.get_id()
        if not id:
            try: id = self.get_parameter('nid')
            except: pass
        if not id:
            error(self, "Cannot set product cache without id")
            return False
        self.set_id(id)
        if id in SPECIAL_PURCHASES:
            self.cache = Cache_purchases()
            self.is_special_purchase = True
        else:
            self.cache = Cache_product(id)
        return True

    def _build_down(self, xbmc_directory, lvl, flag = None, progress = None):
        if not self.set_cache():
            error(self, "Cannot set product cache")
            return False
        data = self.cache.fetch_data(xbmc_directory.Progress)
        if not data:
            warn(self, "Cannot fetch product data")
            return False
        self.set_data(data)
        tracks = None
        if self.is_special_purchase: tracks = self._filter_tracks(data)
        else: tracks = data
        warn (self, pprint.pformat(data))
        for track in tracks['tracks']['items']:
            #rack ['image'] = ""
            # warn(self, "addimagedata")
            node = Node_track()
            node.set_data(track)
            self.add_child(node)

    def _filter_tracks(self, tracks):
        ltracks = []
        id = self.get_id()
        for track in tracks:
            # if track['album']['id'] != id: continue
            ltracks.append(track)
        return ltracks

    def make_XbmcListItem(self):
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
        if a: return int(a)
        a = self.get_property(('interpreter', 'id'))
        if a: return int(a)
        a = self.get_property(('composer', 'id'))
        if a: return int(a)
        return None

    def get_title(self):
        title = self.get_property('title')
        if not title: title = self.get_property('subtitle')
        return title

    def get_image(self):
        image = self.get_property(('image', 'large'))
        image = image.replace('_230.', '_600.')
        if image:
            self.image = image
            return image
        if self.parent:
            image = self.parent.get_image()
            if image: self.image = image
        return self.image

    def get_label(self):
        try:
            label = ''.join((self.get_artist(), ' - ', self.get_title()))
        except: 
            label = self.get_title()
        return label

    def get_label2(self):
        return self.get_label()

    def get_genre(self):
        return self.get_property(('genre', 'name'))

    def get_year(self):
        import time
        date = self.get_property('released_at')
        year = 0
        try: year = time.strftime("%Y", time.localtime(date))
        except: pass
        return year

    def get_description(self):
        return self.get_property('description')

