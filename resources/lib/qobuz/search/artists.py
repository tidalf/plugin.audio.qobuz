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
        data = qobuz.api.search_getResults(query=query, type='artists', limit=limit)
        if not data: return False
        self._raw_data = data
        if not data: return False
        if not 'results' in data: return False
        if len(data['results']['artists']) < 1: return False
        return True



