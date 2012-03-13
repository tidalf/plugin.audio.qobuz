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
        self.SELECT_CURRENT_PLAYLIST = 5
        self.CREATE_PLAYLIST = 6
        self.ADD_TO_CURRENT_PLAYLIST = 7
        self.RENAME_PLAYLIST = 8
        self.REMOVE_PLAYLIST = 9
        self.SCAN = 10
Mode = __Mode()
