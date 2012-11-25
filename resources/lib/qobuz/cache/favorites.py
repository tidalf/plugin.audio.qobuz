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

from icacheable import ICacheable
from constants import *
from debug import *

import qobuz
'''
    Class QobuzPLaylist
'''
class Cache_favorites(ICacheable):

    def __init__(self, id):
        self.id = id
        super(Cache_favorites, self).__init__(qobuz.path.cache,
                                            'favorites',
                                            self.id, False)
        self.set_cache_refresh(qobuz.addon.getSetting('cache_duration_userplaylist'))
        debug(self, "Cache duration: " + str(self.cache_refresh))
        
        self.cacheImage = qobuz.image.cache


    def _fetch_data(self):
        data = qobuz.api.get_favorites(self.id)
        if not data: return None
        return data

    def length(self):
        if not 'tracks' in self._raw_data:
            return 0
        return len(self._raw_data['tracks'])
        
    def get_image(self, name):
        id = 'userplaylist' + name
        return self.cacheImage.get(id)

    def set_image_genre(self, name, image):
        id = 'userplaylist' + name
        return self.cacheImage.set(id, image)
    
    def get_id(self):
        if not self.data:
            return None
        if not 'id' in self.data:
            return None
        if self.data['id']:
            return int(self.data['id'])
        return None