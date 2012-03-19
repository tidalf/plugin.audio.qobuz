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
class Cache_search_artists(ICacheable):

    def __init__(self, name):
        self.name = name
        super(Cache_search_artists, self).__init__(qobuz.path.cache,
                                            'search_artists-' + name.encode('ascii', 'replace'),
                                            None, True)
        self.set_cache_refresh(qobuz.addon.getSetting('cache_duration_userplaylist'))
        info(self, "Cache duration: " + str(self.cache_refresh))

    def _fetch_data(self):
        data = qobuz.api.search_artists(self.name)
        if not data: return None
        if not 'results' in data: return None
        if not 'artists' in data['results']: return None
        return data['results']['artists']

    def length(self):
        if not 'results' in self._raw_data:
            return 0
        return len(self._raw_data['tracks'])
    