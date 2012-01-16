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
from debug import log, info, warn
#from icacheable import ICacheable
import qobuz
"""
 Class QobuzXbmc
"""
class QobuzCore:
    
    def __init__(self):
        self.data = ""
        self.conn = ""
    
    def login(self):
        __addon__ = qobuz.addon
        user =  __addon__.getSetting('username')
        password = __addon__.getSetting('password')
        if not user or not password:
            return False
        info(self, "Try to login as user: " + user)
        return qobuz.api.login( user,
                               __addon__.getSetting('password'))

    def is_logged(self):
        return qobuz.api.userid

    def getPlaylist(self,id):
        from view.playlist import QobuzPlaylist
        return QobuzPlaylist(id)

    def getProduct(self,id, context_type = "playlist"):
        from view.product import QobuzProduct
        return QobuzProduct(id, context_type)

    def getUserPlaylists(self):
        from view.userplaylists import QobuzUserPlaylistsXbmc
        return QobuzUserPlaylistsXbmc()

#    def getQobuzAlbum(self, id):
#        return QobuzAlbum(self, id)

    def getTrack(self,id,context_type="playlist"):
        from data.track import QobuzTrack
        return QobuzTrack(id, context_type)
    
    def getTrackURL(self, id, type):
        from data.track_streamurl import QobuzTrackURL
        return QobuzTrackURL(id, type)
    
    def getQobuzSearchTracks(self):
        from search.tracks import QobuzSearchTracks
        return QobuzSearchTracks()

    def getQobuzSearchAlbums(self):
        from search.albums import QobuzSearchAlbums
        return QobuzSearchAlbums()
    
    def getQobuzSearchArtists(self):
        from search.artists import QobuzSearchArtists
        return QobuzSearchArtists()

    def getProductsFromArtist(self):
        from search.albums import QobuzSearchAlbums
        return QobuzSearchAlbums()

    def getRecommandation(self,genre_id):
        from view.recommandation import QobuzGetRecommandation
        return QobuzGetRecommandation( genre_id)

    def getRecommandation(self, genre_id,type):
        from view.recommandation import QobuzGetRecommandation
        return QobuzGetRecommandation( genre_id, type)
    
    def getPurchases(self):
        from view.purchases import QobuzGetPurchases
        return QobuzGetPurchases()
