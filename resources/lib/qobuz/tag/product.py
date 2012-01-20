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
from tag.track import TagTrack
from tag.genre import TagGenre
from tag.artist import TagArtist

class TagProduct(ITag):
    
    def __init__(self, json, parent = None):
        super(TagProduct, self).__init__(json, parent)
        self.set_valid_tags(['id', 'genre', 'description', 
                            'label', 'price', 'release_date', 'relevancy', 
                            'title', 'type', 'url', 'subtitle', 'goodies', 
                            'release_date', 'awards', 'url', 'added_date', 'length'
                            'added_date', 'released_at', 'subtitle'])
        self.__tracks__ = None
        if json:
            self.parse_json(json)

    def get_tracks(self):
        return self.__tracks__
    
    def getAlbum(self, sep =''):
        album = ''
        try: album = self.subtitle
        except: 
            for c in self.get_childs():
                album = c.getAlbum(sep)
                if album: break
        print "Album: " + album
        return album
    
    def getLabel(self):
        return self.getArtist() +' - '+self.getAlbum()
        
    def getAlbumId(self, sep =''):
        albumid = ''
        try: return self.id
        except: 
            for c in self.get_childs():
                albumid += c.getAlbumId(sep)
                if sep: albumid += sep
        return albumid
                
    def getArtist(self, sep = ''):
        artist = ''
        try: artist = self.artist
        except: pass
        if artist: return artist
        try: artist = self.subtitle
        except: pass
        return artist
    
    def getGenre(self, sep = ''):
        genre = super(TagProduct, self).getGenre()
        if not genre:
            try: genre = self.genre
            except : pass
        return genre
    
    def getDate(self, sep = 0):
        try: 
            return self.release_date
        except: 
            try:
                return self.released_at
            except: pass
        return ''
        
    def getTitle(self, sep = ''):
        title = ''
        try: title =  self.title
        except: pass
        return title
        
    def getAlbum(self, sep = ''):
        album = ''
        try: return self.title
        except:
            for c in self.get_childs():
                album += c.getAlbum(sep)
                if album: return album
        return album

    def getAlbumId(self, sep = ''):
        albumid = ''
        try: return self.id
        except:
            for c in self.get_childs():
                albumid += c.getAlbumId(sep)
                if sep: albumid += sep
        return albumid
    
    def parse_json(self, p):
        self.auto_parse_json(p)
        if 'image' in p:
            self.add_child(TagImage(p['image'], self))
        if 'genre' in p:
            genre = ''
            tag = TagGenre(p['genre'], self)
            genre = tag.getGenre()
            if genre:
                self.add_child(tag)
        if 'artist' in p:
            artist = ''
            if 'name' in p['artist']:
                tag = TagArtist(p['artist'], self)
                artist = tag.getArtist()
                if artist:
                    self.add_child(tag)
            else: 
                self.__dict__['artist'] = p['artist']

        if 'tracks' in p:
            for track in p['tracks']:
                self.add_child(TagTrack(track, self))
        self._is_loaded = True
