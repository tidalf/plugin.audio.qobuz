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
import xbmcgui
import xbmcplugin

import pprint

from mydebug import log, info, warn
from constants import *
from icacheable import ICacheable
from easytag import QobuzTagArtist

"""
    Class QobuzGetRecommendation
"""
class QobuzGetRecommandation(ICacheable):

    def __init__(self, Core, genre_id, type ='new-releases', limit = 100):
        self.Core = Core
        self._raw_data = []
        self.cache_path = os.path.join(self.Core.Bootstrap.cacheDir, 
                                       'recommandations-' 
                                       + genre_id + '-' + type + '.dat')
        self.cache_refresh = self.Core.Bootstrap.__addon__.getSetting('cache_duration_recommandation')
        info(self, "Cache duration: " + str(self.cache_refresh))
        self.genre_id = genre_id
        self.type = type
        self.limit = limit 
        
    def _fetch_data(self):
        return self.Core.Api.get_recommandations(self.genre_id, 
                                                self.type, self.limit)

    def add_to_directory(self):
        data = self.fetch_data()
        n = self.length()
        info(self,"Found " + str(n) + " albums(s)")
        h = int(sys.argv[1])
        u = dir = None

        for p in data:
            #pprint.pprint(p)
            artist = QobuzTagArtist(self.Core, p)
            a=artist.get_album()
            u = sys.argv[0] + "?mode=" + str(MODE_ALBUM) + "&id=" + a.id
            item = xbmcgui.ListItem()
            item.setLabel(artist.getArtist() + ' / ' + a.getTitle() 
                          + " (" + str(a.getYear()) + ")")
            item.setLabel2(a.getTitle())
            item.setInfo(type="Music",infoLabels={ 
                                                  "title": a.getTitle(), 
                                                  "genre": a.getGenre(),
                                                  "year" : int(a.getYear())})
            item.setThumbnailImage(a.getImage())
            xbmcplugin.addDirectoryItem(handle=h, url=u, listitem=item, 
                                        isFolder=True, totalItems=n)
            
        xbmcplugin.addSortMethod(h,xbmcplugin.SORT_METHOD_LABEL)

