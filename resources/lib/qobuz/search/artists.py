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

from constants import *
from debug import log, info, warn
import qobuz
###############################################################################
# Class QobuzSearchArtists
###############################################################################
class Search_artists():

    def __init__(self):
        self._raw_data = []
        
    def get_data(self):
        return self._raw_data
    
    def search(self, query, limit = 100):
        self._raw_data = qobuz.api.search_artists(query, limit)
        return self
        
    def length(self):
        try:
            self._raw_data['results']
        except: return 0
        try:
            self._raw_data['results']['artists']
        except: return 0
        return len(self._raw_data['results']['artists'])
    
    def get_items(self):
        return self._directory_products()
    
    def get_items_by_artist(self):
        return self._directory_products_by_artist()

    def _directory_products(self):
        list = []
        data = self.get_data()
        try:
            data = data['results']['artists']
        except:
            warn(self, "No artist result")
            return list
        image = qobuz.image.access.get('qobuzIcon')
        for json_artist in data:
            tag_artist = TagArtist(json_artist)
            u = qobuz.boot.build_url(MODE_ARTIST, tag_artist.id)
            item   = xbmcgui.ListItem('fanArt')
            item.setLabel(tag_artist.getArtist() )
            item.setProperty('fanart_image', qobuz.image.access.get('fanArt'))
            qobuz.gui.setContextMenu(item)
            list.append((u, item, True))
        return list

    def _directory_products_by_artist():
        list = []
        data = self.get_data()
        artist = None
        try:
            artist = data['artist']['name']
        except:
            warn(self, "No artist result")
        image = qobuz.image.access.get('qobuzIcon')
        for json_album in json['artist']['albums']:
            tag_album = TagAlbum(json_album)
            u = qobuz.boot.build_url(MODE_ALBUM, tag_album.id)
            item = tag_album.getXbmcItem('fanArt')
            if not item.getProperty('fanart_image'):
                item.setProperty('fanart_image', image)
                item.setIconImage( image)
                item.setThumbnailImage(image)
            list.append((u, item, True))
        return list


