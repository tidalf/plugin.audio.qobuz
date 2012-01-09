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

import xbmcaddon
import xbmc

from api import QobuzApi
from mydebug import log, info, warn
#from icacheable import ICacheable

"""
 Class QobuzXbmc
"""
class QobuzCore:
    
    def __init__(self, bootstrap):
        self.Bootstrap = bootstrap
        self.Api = QobuzApi(self)
        self.data = ""
        self.conn = ""
    
    def login(self):
        __addon__ = self.Bootstrap.__addon__
        user =  __addon__.getSetting('username')
        password = __addon__.getSetting('password')
        if not user or not password:
            return False
        info(self, "Try to login as user: " + user)
        return self.Api.login( user,
                               __addon__.getSetting('password'))

    def is_logged(self):
        return self.Api.userid

    def getPlaylist(self,id):
        from playlist import QobuzPlaylist
        return QobuzPlaylist(self, id)

    def getProduct(self,id):
        from product import QobuzProduct
        return QobuzProduct(self, id)

    def getUserPlaylists(self):
        from userplaylists import QobuzUserPlaylists
        return QobuzUserPlaylists(self)

    def getQobuzAlbum(self, id):
        return QobuzAlbum(self, id)

    def getTrack(self,id,context_type="playlist"):
        from track import QobuzTrack
        return QobuzTrack(self,id,context_type)
    
    def getTrackURL(self, id, type):
        from track_streamurl import QobuzTrackURL
        return QobuzTrackURL(self, id, type)
    
    def getQobuzSearchTracks(self):
        from searchtracks import QobuzSearchTracks
        return QobuzSearchTracks(self)

    def getQobuzSearchAlbums(self):
        from searchalbums import QobuzSearchAlbums
        return QobuzSearchAlbums(self)
    
    def getQobuzSearchArtists(self):
        from searchartists import QobuzSearchArtists
        return QobuzSearchArtists(self)

    def getProductsFromArtist(self):
        from searchalbums import QobuzSearchAlbums
        return QobuzSearchAlbums(self)

    def getRecommandation(self,genre_id):
        from getrecommandation import QobuzGetRecommandation
        return QobuzGetRecommandation(self, genre_id)

    def getRecommandation(self, genre_id,type):
        from getrecommandation import QobuzGetRecommandation
        return QobuzGetRecommandation(self, genre_id, type)
    
    def getPurchases(self):
        from getpurchases import QobuzGetPurchases
        return QobuzGetPurchases(self)
