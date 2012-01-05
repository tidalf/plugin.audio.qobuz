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

import xbmcaddon

__addon__ = xbmcaddon.Addon('plugin.audio.qobuz')
__addonname__ = __addon__.getAddonInfo('name')
__cwd__ = __addon__.getAddonInfo('path')
__author__ = __addon__.getAddonInfo('author')
__version__ = __addon__.getAddonInfo('version')
__language__ = __addon__.getLocalizedString
__debugging__ = __addon__.getSetting('debug')

MODE_SEARCH_SONGS = 1
MODE_SEARCH_ALBUMS = 2
MODE_SEARCH_ARTISTS = 3
MODE_SEARCH_ARTISTS_ALBUMS = 4
MODE_SEARCH_PLAYLISTS = 5
MODE_ARTIST_POPULAR = 6
MODE_POPULAR_SONGS = 7
MODE_FAVORITES = 8
MODE_PLAYLISTS = 9
MODE_ALBUM = 10
MODE_ARTIST = 11
MODE_PLAYLIST = 12
MODE_SONG_PAGE = 13
MODE_SIMILAR_ARTISTS = 14
MODE_SHOW_RECOS = 15

MODE_SONG = 30
MODE_FAVORITE = 31
MODE_UNFAVORITE = 32
MODE_MAKE_PLAYLIST = 33
MODE_REMOVE_PLAYLIST = 34
MODE_RENAME_PLAYLIST = 35
MODE_REMOVE_PLAYLIST_SONG = 36
MODE_ADD_PLAYLIST_SONG = 37

ACTION_MOVE_LEFT = 1
ACTION_MOVE_UP = 3
ACTION_MOVE_DOWN = 4
ACTION_PAGE_UP = 5
ACTION_PAGE_DOWN = 6
ACTION_SELECT_ITEM = 7
ACTION_PREVIOUS_MENU = 10

# Formats for track labels
ARTIST_ALBUM_NAME_LABEL = 0
NAME_ALBUM_ARTIST_LABEL = 1

# Stream marking time (seconds)
STREAM_MARKING_TIME = 30

# Timeout
STREAM_TIMEOUT = 30