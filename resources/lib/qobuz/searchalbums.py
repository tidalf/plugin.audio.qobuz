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
import xbmcgui
import xbmcplugin
from utils import _sc
from constants import *
from mydebug import log, info, warn
from easytag import QobuzTagProduct
from easytag import QobuzTagAlbum
from icacheable import ICacheable
import pprint

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
        for product in self.get_data():
            a = QobuzTagProduct(self.Core, product['product'])
            item = a.getXbmcItem()
            u = sys.argv[0] + "?mode=" + str(MODE_ALBUM) + "&id=" + str(a.id)
            item.setPath(u)
            item.setProperty('path', u)
            xbmcplugin.addDirectoryItem(handle=self.Core.Bootstrap.__handle__, 
                                        url=u, listitem=item, isFolder=True, 
                                        totalItems=self.length())
        return self.length()


    def xbmc_directory_products_by_artist(self):
        json = self.get_data()
        h = int(sys.argv[1])
        artist = json['artist']['name']
        for p in json['artist']['albums']:
            a = QobuzTagAlbum(self.Core, p)
            u = sys.argv[0] + "?mode=" + str(MODE_ALBUM) + "&id=" + a.id
            item = xbmcgui.ListItem()
            item.setLabel(a.getTitle() + "(" + str(a.getYear()) + ")")
            item.setInfo(type="Music",infoLabels={"artist" : a.getArtist() })
            item.setThumbnailImage(a.getImage())
            self.Core.Bootstrap.GUI.addDirectoryItem(u , item, True, self.length())
        return self.length()