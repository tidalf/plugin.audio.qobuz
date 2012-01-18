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
import xbmc

#from utils import _sc
from constants import *
from debug import log, info, warn
from utils.tag import QobuzTagTrack
from utils.tag import QobuzTagSearch
import qobuz

###############################################################################
# Class QobuzSearchTracks 
###############################################################################
class QobuzSearchTracks():

    def __init__(self):
        self._raw_data = {}
        
    def search(self, query, limit = 100):
        self._raw_data = qobuz.api.search_tracks(query, limit)
        return self
        
    def length(self):
        if not self._raw_data['results']:
            return 0
        return len(self._raw_data['results']['tracks'])
    
    def get_items(self):
        ts = QobuzTagSearch(self._raw_data['results'])
        childs = ts.get_childs()
        list = []
        for track in childs:
            item = track.getXbmcItem('playlist', 'fanArt')
            u = qobuz.boot.build_url(MODE_SONG, int(track.id))
            list.append((u, item, False))
        return list


