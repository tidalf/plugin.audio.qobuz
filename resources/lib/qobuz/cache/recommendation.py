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
import random
import xbmcgui
import xbmcplugin

import pprint

from debug import *
from constants import *
from icacheable import ICacheable
import qobuz
"""
    Class QobuzGetRecommendation
"""
class Cache_recommendation(ICacheable):

    def __init__(self, genre_id, type = 'new-releases', limit = 100):
        self.genre_id = genre_id
        self.type = type
        self.limit = limit
        super(Cache_recommendation, self).__init__(qobuz.path.cache,
                                                     'recommendations-' + type,
                                                     genre_id)
        self.set_cache_refresh(qobuz.addon.getSetting('cache_duration_recommendation'))
        debug(self, "Cache duration: " + str(self.cache_refresh))
        self.cacheImage = qobuz.image.cache
        self.fetch_data()

    def _fetch_data(self):
        return qobuz.api.get_recommandations(self.genre_id,
                                             self.type,
                                             self.limit)['albums']['items']
    def length(self):
        return len(self.get_raw_data())

    def get_image(self):
        return self.cacheImage.get(self.type + str(self.genre_id))

    def set_image_genre(self, image):
        return self.cacheImage.set(self.type + str(self.genre_id), image)

