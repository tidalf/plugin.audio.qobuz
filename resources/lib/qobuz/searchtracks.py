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
import xbmcgui
import xbmcplugin
from utils import _sc
from constants import *
from mydebug import log, info, warn
from easytag import QobuzTagTrack
import pprint

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
        for track in self._raw_data['results']['tracks']:
            t = QobuzTagTrack(track)
            item = t.getXbmcItem('songs')
            u = sys.argv[0] + "?mode=" + str(MODE_SONG) + "&id=" + t.id
            if 1:
                action="XBMC.RunPlugin("+sys.argv[0]+"?mode="+str(MODE_ALBUM)+"&id="+str(t.get_album().id)+")"
                print "Show Album: " + action
                item.addContextMenuItems([('Show album', action)], False)
            self.Core.Bootstrap.GUI.addDirectoryItem(u , item, False, n)


