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
import os
import xbmcgui
import xbmcplugin

import pprint

from debug import log, info, warn
from constants import *
from utils.icacheable import ICacheable
from utils.tag import QobuzTagArtist
from utils.tag import QobuzTagTrack
from utils.tag import QobuzTagProduct
import qobuz
"""
    Class QobuzGetPurchases
"""
class QobuzGetPurchases(ICacheable):

    def __init__(self, limit = 100):
        self.limit = limit
        super(QobuzGetPurchases, self).__init__(qobuz.path.cache, 
                                       'purchases')
        self.set_cache_refresh(qobuz.addon.getSetting('cache_duration_recommandation'))
        info(self, "Cache duration: " + str(self.cache_refresh))
        self.fetch_data()
        
    def _fetch_data(self):
        return qobuz.api.get_purchases(self.limit)
    
    def length(self):
        if not self._raw_data:
            return 0
        return len(self._raw_data)

    def get_items(self):
        n = self.length()
        albumseen = {}
        needsave = False
        list = []
        for track in self._raw_data:   
            t = QobuzTagTrack(track)
            if 'BLACK_ID' in track:
                continue
            albumid = t.getAlbumId()
            isseen = 'false'
            if albumid in albumseen:
                continue
            if isseen == 'false':
                log ('warn','album never seen try to add it')
                try:
                    album = qobuz.core.getProduct(str(albumid))
                except:
                    track['BLACK_ID'] = 'true'
                    needsave = True
                    continue
                a = QobuzTagProduct(album.get_raw_data())
                item = a.getXbmcItem()
                albumid = a.id     
                
                u = qobuz.boot.build_url(MODE_ALBUM, albumid)
                list.append((u, item, True))        
                albumseen[albumid] = 'true'
        if needsave:
            self._save_cache_data(self._raw_data)
        return list

