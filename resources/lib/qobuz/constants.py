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

__debugging__ = 0

class __Mode():
    def __init__(self):
        self.VIEW = 1
        self.PLAY = 2
        self.ERASE_CACHE = 3
        self.LIBRARY_SCAN = 4
        self.SCAN = 10
        self.VIEW_BIG_DIR = 11
        ''' Playlist '''
        self.PLAYLIST_REMOVE_TRACK = 12
        self.PLAYLIST_SELECT_CURRENT = 13 
        self.PLAYLIST_ADD_TO_CURRENT = 14    
        self.PLAYLIST_CREATE = 15
        self.PLAYLIST_RENAME = 16
        self.PLAYLIST_REMOVE = 17
        self.PLAYLIST_ADD_AS_NEW = 18

    
    def to_s(self, mode):
        if mode == self.VIEW: return "view"
        elif mode == self.PLAY: return "play"
        elif mode == self.ERASE_CACHE: return "clear cache"
        elif mode == self.LIBRARY_SCAN: return "library scan"
        elif mode == self.SCAN: return "scan"
        elif mode == self.VIEW_BIG_DIR: return "view big dir"
        elif mode == self.PLAYLIST_REMOVE: return "playlist remove"
        elif mode == self.PLAYLIST_REMOVE_TRACK: return "playlist remove track"
        elif mode == self.PLAYLIST_CREATE: return "playlist create"
        elif mode == self.PLAYLIST_RENAME: return "playlist rename"
        # elif mode == self.PLAYLIST_ADD_AS_NEW: return "playlist add as new"
        elif mode == self.PLAYLIST_ADD_TO_CURRENT: return "playlist add to current"
        elif mode == self.PLAYLIST_SELECT_CURRENT: return "playlist select current"
        else: return "Unknow mode: " + str(mode)
        
Mode = __Mode()
