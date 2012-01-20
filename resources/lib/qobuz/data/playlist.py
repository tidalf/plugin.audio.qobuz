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

import os
import sys
import random

from utils.icacheable import ICacheable
from constants import *
from debug import * 
from tag.playlist import TagPlaylist
from tag.track import TagTrack
import qobuz
'''
    Class QobuzPLaylist
'''
class QobuzPlaylist(ICacheable):

    def __init__(self,id):
        self.id = id
        super(QobuzPlaylist, self).__init__(qobuz.path.cache,
                                            'playlist',
                                            self.id)
        self.set_cache_refresh(qobuz.addon.getSetting('cache_duration_userplaylist'))
        info(self, "Cache duration: " + str(self.cache_refresh))
        self.cacheImage = qobuz.image.cache
        

    def _fetch_data(self):
        data = qobuz.api.get_playlist(self.id)
        if not data: return None
        return data['playlist']

    def length(self):
        if not 'tracks' in self._raw_data:
            return 0
        return len(self._raw_data['tracks'])

    def get_image(self, name):
        return self.cacheImage.get('userplaylists', name)
    
    def set_image_genre(self, name, image):
        return self.cacheImage.set('userplaylists', name, image)
    
    def get_items(self):
        self.fetch_data()
        list = []
        n = self.length()
        if n < 0:
            return list
        p = TagPlaylist(self.get_data())
        rand = random.randint(0, n)
        needimage = False
        if not self.get_image(p.name):
            needimage = True
        i = 0
        for t in p.get_childs():
            if not isinstance(t, TagTrack):
                continue
            item = t.getXbmcItem('playlist')
            if needimage and i == rand:
                self.set_image_genre(p.id, t.getImage())
                needimage = False
            u = qobuz.boot.build_url(MODE_SONG, str(t.id))
            item.setPath(u) 
            list.append((u, item, False))
            i += 1
        return list
