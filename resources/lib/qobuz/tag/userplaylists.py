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

class TagUserPlaylists(ITag):
    
    def __init__(self, json):
        super(TagUserPlaylists, self).__init__(json)
        self.set_valid_tags(['id', 'name', 'description', 'position', 
                             'created_at', 'updated_at', 'is_public', 
                             'is_collaborative', 'owner_id', 'owner_name', 'length'])
        if json:
            self.parse_json(json)
    
    def parse_json(self, p):
        self.set('id', p['id'])
        self.set('name', p['name'])
        self.set('description', p['description'])
        try:
            self.set('position', p['position'])
        except: pass
        try:
            self.set('created_at', p['created_at'])
        except: pass
        try:
            self.set('updated_at', p['updated_at'])
        except: pass
        self.set('is_public', p['is_public'])
        self.set('is_collaborative', p['is_collaborative'])
        self.set('owner_id', p['owner']['id'])
        self.set('owner_name', p['owner']['name'])
        try:
            p['length']
            self.set('length', p['length'])
        except:
            self.set('length', '-1')
        self._is_loaded = True
