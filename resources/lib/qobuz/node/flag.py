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

from exception import QobuzXbmcError

class __NodeFlag():
    def __init__(self):
        self.DONTFETCHTRACK        = 1
        self.NODE             = 2
        self.TRACK            = 4
        self.PLAYLIST         = 8
        self.USERPLAYLISTS    = 16
        self.RECOMMENDATION   = 32
        self.ROOT             = 64
        self.PRODUCT          = 128
        self.PURCHASES        = 256
        self.SEARCH           = 512
        self.ARTIST           = 1024
        self.SIMILAR_ARTIST   = 2048
        self.FAVORITES        = 4096
        self.CUSTOM_SEARCH    = 8192
        self.FRIEND           = 16384
        self.FRIEND_LIST      = 32768
        self.GENRE            = 65536
        self.LABEL            = 131072    
        self.PAGINATION       = 262144       
        
    def to_s(self, flag):
        if flag   & self.TRACK: return "track"
        elif flag & self.PLAYLIST: return "playlist"
        elif flag & self.USERPLAYLISTS: return "user_playlists"
        elif flag & self.RECOMMENDATION: return "recommendation"
        elif flag & self.ROOT: return "root"
        elif flag & self.PRODUCT: return "product"
        elif flag & self.PURCHASES: return "purchases"
        elif flag & self.FAVORITES: return "favorites"
        elif flag & self.SEARCH: return "search"
        elif flag & self.ARTIST: return "artist"
        elif flag & self.SIMILAR_ARTIST: return "similar_artist" 
        elif flag & self.FRIEND: return "friend"
        elif flag & self.FRIEND_LIST: return "friend_list"
        elif flag & self.GENRE: return "genre"
        elif flag & self.LABEL: return "label"
        elif flag & self.NODE: return "node"
        elif flag & self.DONTFETCHTRACK: return "dont_fetch_track"
        else: raise QobuzXbmcError(who=self, what='invalid_flag', additional=repr(flag))
        
NodeFlag = __NodeFlag()

