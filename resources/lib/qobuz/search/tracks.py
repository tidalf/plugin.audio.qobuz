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

###############################################################################
# Class QobuzSearchTracks 
###############################################################################
class QobuzSearchTracks():

    def __init__(self, Core):
        self.Core = Core
        self._raw_data = {}
        
    def search(self, query, limit = 100):
        self._raw_data = self.Core.Api.search_tracks(query, limit)
        return self
        
    def length(self):
        if not self._raw_data['results']:
            return 0
        return len(self._raw_data['results']['tracks'])
    
    def add_to_directory(self):
        n = self.length()
        xp = self.Core.Bootstrap.Player.Playlist
        xp.clear()
        i = 0
        ts = QobuzTagSearch(self.Core, self._raw_data['results'])
        childs = ts.get_childs()
        for track in childs:
            item = track.getXbmcItem('playlist')
            u = self.Core.Bootstrap.build_url(MODE_SONG, int(track.id), i)
            self.Core.Bootstrap.GUI.addDirectoryItem(u , item, False, n)
            item.setProperty("Music", 'true')
            item.setProperty('IsPlayable', 'false')
            xp.add(u, item)
            i = i + 1
        return n


