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

from itag import ITag
from image import Tag_image
from label import Tag_label
from genre import Tag_genre

class Tag_album(ITag):
    
    def __init__(self, json):
        super(Tag_album, self).__init__(json)
        self.set_valid_tags(['id', 'title', 'genre', 'label', 
                             'release_date', 'released_at'])
        if json:
            self.parse_json(json)
    
    def parse_json(self, p):
        self.auto_parse_json(p)
        if 'image' in p:
            image = Tag_image(p['image'])
            self.add_child(image)
        if 'label' in p:
            label = Tag_label(p['label'])
            self.add_child(label)
        if 'genre' in p:
            genre = Tag_genre(p['genre'])
            self.add_child(genre)
        
        self._is_loaded = True
        
    def getAlbum(self, sep = ''):
        try: return self.title
        except: return ''
    
    def getAlbumId(self, sep = ''):
        try: return self.id
        except: return ''
    
    def getTitle(self, sep = ''):
        try: return self.title
        except: return ''
        
    def getDate(self, sep = ''):
        try: return self.release_date
        except:
            try: return self.released_date
            except: return ''
    
    def getId(self, sep = ''):
        try: return self.id
        except: return ''        