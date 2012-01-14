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
import xbmcplugin

from constants import *
from debug import log, info, warn
from utils.tag import QobuzTagProduct
from utils.tag import QobuzTagAlbum
from utils.icacheable import ICacheable

'''
    Class QobuzSearchAlbums
'''
class QobuzSearchAlbums():

    def __init__(self, Core,):
        self.Core = Core
        self._raw_data = []
        
    def get_data(self):
        return self._raw_data
    
    def search(self, query, limit = 100):
        self._raw_data = self.Core.Api.search_albums(query, limit)
        return self
    
    def get_by_artist(self,id, limit = 100):
        self._raw_data = self.Core.Api.get_albums_from_artist(id, limit)
        return self
        
    def length(self):
        return len(self._raw_data)
    
    def add_to_directory(self):
        return self.xbmc_directory_products()
    
    def add_to_directory_by_artist(self):
        return self.xbmc_directory_products_by_artist()

    def xbmc_directory_products(self):
        n = self.length()
        for product in self.get_data():
            tag_product = QobuzTagProduct(product['product'])
            item = tag_product.getXbmcItem()
            u = self.Core.Bootstrap.build_url(MODE_ALBUM, tag_product.id)
            xbmcplugin.addDirectoryItem(handle=self.Core.Bootstrap.__handle__, 
                                        url=u, listitem=item, isFolder=True, 
                                        totalItems=n)
        return n

    def xbmc_directory_products_by_artist(self):
        n = self.length()
        json = self.get_data()
        h = int(sys.argv[1])
        artist = json['artist']['name']
        for json_album in json['artist']['albums']:
            tag_product = QobuzTagProduct(json_album)
            u = self.Core.Bootstrap.build_url(MODE_ALBUM, tag_product.id)
            item = tag_product.getXbmcItem()
            self.Core.Bootstrap.GUI.addDirectoryItem(u , item, True, n)
        return n
