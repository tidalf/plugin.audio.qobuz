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

from constants import *
from debug import log, info, warn
from utils.tag import QobuzTagProduct
from utils.tag import QobuzTagAlbum
from utils.icacheable import ICacheable
import qobuz
'''
    Class QobuzSearchAlbums
'''
class QobuzSearchAlbums():

    def __init__(self):
        self._raw_data = []
        
    def get_data(self):
        return self._raw_data
    
    def search(self, query, limit = 100):
        self._raw_data = qobuz.api.search_albums(query, limit)
        return self
    
    def search_by_artist(self,id, limit = 100):
        self._raw_data = qobuz.api.get_albums_from_artist(id, limit)
        return self
        
    def length(self):
        return len(self._raw_data)
    
    def get_items(self):
        return self._directory_products()
    
    def get_items_by_artist(self):
        return self._directory_products_by_artist()

    def _directory_products(self):
        list = []
        data = self.get_data()
        if not data:
            return list
        for product in self.get_data():
            tag_product = QobuzTagProduct(product['product'])
            item = tag_product.getXbmcItem('fanArt')
            u = qobuz.boot.build_url(MODE_ALBUM, tag_product.id)
            list.append((u, item, True))
        return list

    def _directory_products_by_artist(self):
        json = self.get_data()
        artist = None
        list = []
        try:
            artist = json['artist']['name']
        except:
            return list
        for json_album in json['artist']['albums']:
            tag_product = QobuzTagProduct(json_album)
            u = qobuz.boot.build_url(MODE_ALBUM, tag_product.id)
            item = tag_product.getXbmcItem('fanArt')
            list.append((u, item, True))
        return list
