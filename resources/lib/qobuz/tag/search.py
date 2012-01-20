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

from tag.itag import ITag
from tag.track import TagTrack

class TagSearch(ITag):
    
    def __init__(self, json):
        super(TagSearch, self).__init__(json)
        self.__tracks__ = []
        if json:
            self.parse_json(json)
        
    def parse_json(self, p):
        for track in p['tracks']:
            self.add_child(TagTrack(track, self))
        self._is_loaded = True