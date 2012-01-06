# Copyright 2011 Joachim Basmaison, Cyril Leclerc

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

import pprint

from easytag import QobuzTagTrack

###############################################################################
# Class QobuzSearchArtists
###############################################################################
class QobuzSearchArtists():

    def __init__(self, qob,):
        self.Qob = qob
        self._raw_data = []
        
    def search(self, query, limit = 100):
        self._raw_data = self.Qob.Api.search_artists(query, limit)
        return self
        
    def length(self):
        try:
            self._raw_data['results']
        except: return 0
        try:
            self._raw_data['results']['artists']
        except: return 0
        return len(self._raw_data['results']['artists'])
    
    def add_to_directory(self):
        h = int(sys.argv[1])
        xbmc_directory_products(self._raw_data, self.length())
        xbmcplugin.setContent(h,'artists')

def xbmc_directory_products(json, len):
      h = int(sys.argv[1])
      for p in json['results']['artists']:
         artist = _sc(p['name'])
         u = sys.argv[0] + "?mode=" + str(MODE_ARTIST) + "&id=" + str(p['id'])
         item   = xbmcgui.ListItem()
         item.setLabel(artist.encode("utf8","ignore"))
         xbmcplugin.addDirectoryItem(handle=h , url=u,listitem=item,isFolder=True,totalItems=len)
