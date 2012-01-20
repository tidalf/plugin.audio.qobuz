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
from tag.image import TagImage
from tag.label import TagLabel
from tag.genre import TagGenre

class TagAlbum(ITag):
    
    def __init__(self, json):
        super(TagAlbum, self).__init__(json)
        self.set_valid_tags(['id', 'title', 'genre', 'label', 
                             'release_date', 'released_at'])
        if json:
            self.parse_json(json)
    
    def parse_json(self, p):
        self.auto_parse_json(p)
        if 'image' in p:
            image = TagImage(p['image'])
            self.add_child(image)
        if 'label' in p:
            label = TagLabel(p['label'])
            self.add_child(label)
        if 'genre' in p:
            genre = TagGenre(p['genre'])
            self.add_child(genre)
        
        self._is_loaded = True
        
    def getAlbum(self, sep = ''):
        try:
            return self.title
        except: return ''
    
    def getAlbumId(self, sep = ''):
        try:
            return self.id
        except: return ''
    
    def getTitle(self, sep = ''):
        try: return self.title
        except: return ''
        
    def getDate(self, sep = ''):
        try:
            return self.release_date
        except:
            try: 
                return self.released_date
            except:
                return ''
    def getId(self, sep = ''):
        try: 
            return self.id
        except:
            return ''        