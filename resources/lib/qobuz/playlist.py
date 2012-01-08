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
import xbmc
import xbmcgui
import xbmcplugin

from icacheable import ICacheable
from utils import _sc
from constants import *
from mydebug import * 
from easytag import QobuzTagPlaylist

'''
    Class QobuzPLaylist
'''
class QobuzPlaylist(ICacheable):

    def __init__(self, Core, id):
        self.Core = Core
        self.id = id
        self._raw_data = []
        self.cache_path = os.path.join(
                                        self.Core.Bootstrap.cacheDir,
                                        'playlist-' + str(self.id) + '.dat')
        self.cache_refresh = self.Core.Bootstrap.__addon__.getSetting('cache_duration_userplaylist')
        info(self, "Cache duration: " + str(self.cache_refresh))
        self.fetch_data()

    def _fetch_data(self):
        data = self.Core.Api.get_playlist(self.id)['playlist']
        return data

    def length(self):
        return len(self._raw_data['tracks'])

    def add_to_directory(self):
        n = self.length()
        h = int(sys.argv[1])
        p = QobuzTagPlaylist(self.get_data())
        for t in p.get_tracks():
            item = t.getXbmcItem('playlist')
            image = t.get_album().getImage()
            if image:
                item.setThumbnailImage(image)
                item.setIconImage(image)
            u = sys.argv[0] + "?mode=" + str(MODE_SONG) + "&id=" + t.id    
            xbmcplugin.addDirectoryItem(handle=h ,url=u ,listitem=item,isFolder=False,totalItems=n)
        xbmcplugin.setContent(h,'songs')
