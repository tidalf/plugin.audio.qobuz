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

import tempfile

from icacheable import ICacheable
from api import QobuzApi
from mydebug import log, info, warn
from utils import _sc
from track import QobuzTrack
from icacheable import ICacheable
from getrecommandation import QobuzGetRecommandation
from product import QobuzProduct
from userplaylists import QobuzUserPlaylists
from playlist import QobuzPlaylist
from searchtracks import QobuzSearchTracks
from searchalbums import QobuzSearchAlbums
from searchartists import QobuzSearchArtists
from time import time
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
        info(self, "Try to login as user: " + user)
        return self.Api.login( user,
                               __addon__.getSetting('password'))

    def is_logged(self):
        return self.Api.userid

    def getPlaylist(self,id):
        return QobuzPlaylist(self, id)

    def getProduct(self,id):
        return QobuzProduct(self, id)

    def getUserPlaylists(self):
        return QobuzUserPlaylists(self)

    def getQobuzAlbum(self, id):
        return QobuzAlbum(self, id)

    def getTrack(self,id):
        return QobuzTrack(self,id)
    
    def getEncounteredAlbum(self):
        return QobuzEncounteredAlbum(self)
    
    def getQobuzSearchTracks(self):
        return QobuzSearchTracks(self)

    def getQobuzSearchAlbums(self):
        return QobuzSearchAlbums(self)
    
    def getQobuzSearchArtists(self):
        return QobuzSearchArtists(self)

    def getProductsFromArtist(self):
        return QobuzSearchAlbums(self)

    def watchPlayback( self ):
        if not self.player.isPlayingAudio():
            self.Timer.stop()
            exit(0)
        info(self, "Watching player: " + self.player.getPlayingFile())
        self.Timer = threading.Timer( 6, self.watchPlayback, () )
        self.Timer.start()

    def getRecommandation(self,genre_id):
        return QobuzGetRecommandation(self, genre_id)

    def getRecommandation(self, genre_id,type):
        return QobuzGetRecommandation(self, genre_id, type)
