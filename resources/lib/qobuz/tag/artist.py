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

class TagArtist(ITag):
    
    def __init__(self, json, parent = None):
        super(TagArtist, self).__init__(json, parent)
        self.set_valid_tags(['id', 'name'])
        if json: self.auto_parse_json(json)

    def getArtist(self, sep = ''):
        try: return self.name
        except: return ''        
        
    def getArtistId(self, sep = ''):
        try: return self.id
        except: return ''