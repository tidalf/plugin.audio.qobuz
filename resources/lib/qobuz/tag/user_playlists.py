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
import pprint

from tag.itag import ITag
from tag.owner import Tag_owner
from cache.user_playlists import Cache_user_playlists

class Tag_user_playlists(ITag):
    
    def __init__(self):
        super(Tag_user_playlists, self).__init__()
        self.set_valid_tags(['id', 'name', 'description', 'position', 
                             'created_at', 'updated_at', 'is_public', 
                             'is_collaborative', 'length'])
        
        self.cache = Cache_user_playlists()

    def parse_json(self, json):
        self.auto_parse_json(json)
        return True
        

