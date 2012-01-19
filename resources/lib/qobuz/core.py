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
import qobuz

"""
 Class QobuzXbmc
"""
class QobuzCore:
    
    def __init__(self):
        self.data = ""
        self.conn = ""
    
    def login(self):
        username = qobuz.addon.getSetting('username')
        password = qobuz.addon.getSetting('password')
        if not username or not password:
            return False
        auth =  qobuz.api.login(username, password)
        if not auth: return False
        if auth.get_data()['user']['login'] != username:
            warn(self, "User login mismatch")
            auth.delete_cache()
            self.delete_user_data()
            return False
        return auth

    def delete_user_data(self):
        try: 
            from utils.cache import cache_manager
            c = cache_manager()
            c.delete_user_data()
        except:
            warn(self, "Cannot remove user data from cache")

    def is_logged(self):
        return qobuz.api.auth

    def getPlaylist(self,id):
        from data.playlist import QobuzPlaylist
        return QobuzPlaylist(id)

    def getProduct(self,id, context_type = "playlist"):
        from data.product import QobuzProduct
        return QobuzProduct(id, context_type)

    def getUserPlaylists(self):
        from data.userplaylists import QobuzUserPlaylistsXbmc
        return QobuzUserPlaylistsXbmc()

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
        from data.recommandation import QobuzGetRecommandation
        return QobuzGetRecommandation( genre_id)

    def getRecommandation(self, genre_id,type):
        from data.recommandation import QobuzGetRecommandation
        return QobuzGetRecommandation( genre_id, type)
    
    def getPurchases(self):
        from data.purchases import QobuzGetPurchases
        return QobuzGetPurchases()
