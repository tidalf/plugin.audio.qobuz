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
import qobuz
from debug import log, info, warn

'''
    Class QobuzSearchAlbums
'''
class Search_albums():

    def __init__(self):
        self._raw_data = []

    def get_data(self):
        return self._raw_data

    def search(self, query, limit = 100):
        data = qobuz.api.search_getResults(query=query, type='albums', limit=limit)
        if not data: return False
        self._raw_data = data
        if len(data) > 0: return True
        return False

    def search_by_artist(self, p_id, limit = 100):
        self._raw_data = qobuz.api.get_albums_from_artist(p_id, limit)
        return self

