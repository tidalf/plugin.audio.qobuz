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

###############################################################################
# Class QobuzSearchAlbums
###############################################################################
class QobuzSearchAlbums():

    def __init__(self, qob,):
        self.Qob = qob
        self._raw_data = []
        
    def search(self, query, limit = 100):
        self._raw_data = self.Qob.Api.search_albums(query, limit)
        #pprint.pprint(self._raw_data)
        return self
    
    def get_by_artist(self,id, limit = 100):
        self._raw_data = self.Qob.Api.get_albums_from_artist(id, limit)
        #pprint.pprint(self._raw_data)
        return self
        
    def length(self):
        return len(self._raw_data)
    
    def add_to_directory(self):
        h = int(sys.argv[1])
        xbmc_directory_products(self._raw_data, self.length())
        #xbmcplugin.addDirectoryItem(handle=h ,url=u ,listitem=item,isFolder=False,totalItems=n)
        xbmcplugin.setContent(h,'songs')
    
    def add_to_directory_by_artist(self):
        h = int(sys.argv[1])
        xbmc_directory_products_by_artist(self._raw_data, self.length())
        #xbmcplugin.addDirectoryItem(handle=h ,url=u ,listitem=item,isFolder=False,totalItems=n)
        xbmcplugin.setContent(h,'songs')
 
 
def xbmc_directory_products(json, len):
    h = int(sys.argv[1])
    for p in json:
        a      = p['product']
        title  = _sc(a['title'])
        artist = _sc(a['artist'])
        genre  = _sc(a['genre'])
        image  = a['image']['large']
        year   = int(a['release_date'].split('-')[0]) if a['release_date'] else 0
        u = sys.argv[0] + "?mode=" + str(MODE_ALBUM) + "&id=" + str(a['id'])
        #(sh,sm,ss) = a['duration'].split(':')
        item   = xbmcgui.ListItem()
        item.setLabel(genre + ' / ' + artist + ' - ' + title)
        item.setInfo(type="Music",infoLabels={
                                                   #"count"  : long(a['id']),
                                                   "artist" : artist,
#                                                   "album"  : title,
#                                                   "genre"  : genre,
#                                                   "comment": "Qobuz Stream",
#                                                   "year"   : year
        })
        print "U:" + u + "\n"
        #item.setPath(u)
        #item.setProperty('Music','true')
        #item.setProperty('IsPlayable','false');
        item.setThumbnailImage(image)
        xbmcplugin.addDirectoryItem(handle=h , url=u,listitem=item,isFolder=True,totalItems=len)

def xbmc_directory_products_by_artist(json, len):
    h = int(sys.argv[1])
    artist = json['artist']['name']
    for p in json['artist']['albums']:
        a      = p
        title  = _sc(a['title'])
#        genre  = _sc(a['genre'])
        image  = a['image']['large']
        year   = int(a['released_at'].split('-')[0]) if a['released_at'] else 0
        u = sys.argv[0] + "?mode=" + str(MODE_ALBUM) + "&id=" + str(a['id'])
        #(sh,sm,ss) = a['duration'].split(':')
        item   = xbmcgui.ListItem()
        item.setLabel(title + "(" + str(year) + ")")
        item.setInfo(type="Music",infoLabels={
                                                   #"count"  : long(a['id']),
                                                   "artist" : artist,
#                                                   "album"  : title,
#                                                   "genre"  : genre,
#                                                   "comment": "Qobuz Stream",
#                                                   "year"   : year
        })
        print "U:" + u + "\n"
        #item.setPath(u)
        #item.setProperty('Music','true')
        #item.setProperty('IsPlayable','false');
        item.setThumbnailImage(image)
        xbmcplugin.addDirectoryItem(handle=h , url=u,listitem=item,isFolder=True,totalItems=len)

