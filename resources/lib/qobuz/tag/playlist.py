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

class TagPlaylist(ITag):
    
    def __init__(self, json, parent = None):
        super(TagPlaylist, self).__init__(json, parent)
        self.set_valid_tags(['name', 'id', 'is_collaborative', 'is_public'])
        if json:
            self.parse_json(json)
    
    def getLabel(self):
        name = ''
        try:
            name = self.owner + ' - ' + self.name
        except: pass
        ispub = ''
        try:
            ispub = '[prv] '
            if self.is_public:
                ispub = '[pub] ' 
        except: pass
        return ispub + name
    
    def parse_json(self, p):
        self.auto_parse_json(p)
        self.set('owner', p['owner']['name'])
        if not 'tracks' in p:
            return 
        for track in p['tracks']:
            self.add_child(TagTrack(track, self))
        self._is_loaded = True