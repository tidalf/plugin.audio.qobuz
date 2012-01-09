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
import sys
from constants import *
import xbmcgui
import xbmcaddon
from mydebug import warn, info, log

import pprint

class IQobuzTag(object):
    
    def __init__(self, Core, json = None):
        self.__valid_tags = None
        self.__is_loaded = None
        self._json = json
        self.Core = Core
        
    def parse_json(self, json):
        assert("load_json must be overloaded")
    
    def set_valid_tags(self, tags):
        self.__valid_tags = tags
    
    def get(self, key):
        if not self.is_loaded():
            assert("Json is not loaded")
        if key not in self.__valid_tags:
            assert("Invalid tag: " + key)
        return self.__dict__[key]
    
    def set(self, key, value):
        if key not in self.__valid_tags:
            assert("Invalid tag:" + key)
        v = ''
        try:
            v = str(value)
        except:
            if isinstance(value, basestring):
                v = value.encode('utf8', 'ignore')
            elif isinstance(value, bool):
                if value: v = '1'
                else: v = '0'
        self.__dict__[key] = v
    
    def is_loaded(self):
        return self.__is_loaded
    
    def getTitle(self):
        v = 'N/A'
        try:
            v = self.title
        except: pass
        return v
    
    def get_album(self):
        return None
    
    def getArtist(self):
        label = ''
        try:
            label = self.artist
        except: pass
        if label: return label
        try:
            label = self.interpreter_name
        except: pass
        if label: return label
        try:
            label =  self.composer_name
        except: pass
        if label: return label
        return 'N/A'
    
    def getArtistId(self):
        label = []
        try: 
            label.append(self.artist_id)
        except:
            try:
                label.append(self.interpreter_id)
            except: 
                try:
                    label.append(self.composer_id)
                except: label.append('N/A')
        return ''.join(label)
    
    def getGenre(self):
        genre = ''
        try:
            genre = self.genre
        except:
            genre = 'N/A'
        return genre
    
    def getDuration(self):
        try:
            (sh,sm,ss) = self.duration.split(':')
        except:
            return 0
        return (int(sh) * 3600 + int(sm) * 60 + int(ss))
    
    def getYear(self):
        date = 0
        try:
            date = self.release_date
        except:
            try:
                date = self.released_at
            except:
                try:
                    date = self.created_at
                except: pass
        if not date:
            return date
        year = 0
        try: 
            year = int(date.split('-')[0])
        except: pass
        return year
    
    def getImage(self):
        image = ''
        if self.get_album():
            image = self.get_album().getImage()
        if image:
            return image
        try:
            image = self.image_large
        except:
            try:
                image = self.image_small
            except:
                try:
                    image = self.image_thumbnail
                except: pass
        return image
    
    def getTracknumber(self):
        tn = 0
        try:
            tn = self.track_number
        except:
            return 0
        return tn
    
    def getStreamingType(self):
        st = ''
        try:
            st = self.streaming_type
        except: pass
        return st
    
    def getXbmcItem(self):
        i = xbmcgui.ListItem(self.getTitle())
        album = ''
        try:
            album = self.get_album().getTitle()
        except: pass
        i.setInfo(type='music', infoLabels = {
                                             'title': self.getTitle(),
                                             'artist': self.getArtist(),
                                             'genre': self.getGenre(),
                                             'tracknumber': int(self.getTracknumber()),
                                             'album': album,
                                             'duration': int(self.getDuration()),
                                             'year': int(self.getYear()),
                                             'comment': 'Qobuz Music Streaming (qobuz.com)'
                                             })
        image = ''
        try:
            image = self.getImage()
        except:
            pass
        if image:
            i.setThumbnailImage(image)
            i.setIconImage(image)
            i.setProperty('image', image)
        return i
'''
'''
class QobuzTagUserPlaylist(IQobuzTag):
    
    def __init__(self, Core, json):
        super(QobuzTagUserPlaylist, self).__init__(Core, json)
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

class QobuzTagArtist(IQobuzTag):
    
    def __init__(self, Core, json):
        super(QobuzTagArtist, self).__init__(Core, json)
        self.set_valid_tags(['id', 'name'])
        self.__album = None
        if json:
            self.parse_json(json)

        
    def getArtist(self):
        try:
            return self.name
        except:
            return supper(QobuzTagArtis, self).getArtist()
    
    def get_album(self):
        return self.__album
    
    def parse_json(self, p):
        self.set('id', p['id'])
        try:
            self.set('name', p['artist']['name'])
        except:
            try:
                self.set('name', p['name'])
            except: pass
        try:
            self.__album = QobuzTagAlbum(self.Core, p)
        except:
            pass
        self._is_loaded = True
        
'''
'''
class QobuzTagAlbum(IQobuzTag):
    
    def __init__(self, Core, json):
        super(QobuzTagAlbum, self).__init__(Core, json)
        self.set_valid_tags(['id', 'title', 'genre', 'label', 'image_large', 
                             'release_date'])
        if json:
            self.parse_json(json)
    
    def parse_json(self, p):
        self.set('id', p['id'])
        self.set('title', p['title'])
        try:
            self.set('label', p['label'])
        except: pass
        try:
            self.set('genre', p['genre']['name'])
        except: pass
        try:
            self.set('image_large', p['image']['large'])
        except: pass
        try:
            self.set('release_date', p['release_date'])
        except:
            try:
                self.set('released_at', p['released_at'])
            except: pass
        try:
            self.set('subtitle', p['subtitle'])
        except: pass
        self._is_loaded = True

'''
'''
class QobuzTagProduct(IQobuzTag):
    
    def __init__(self, Core, json):
        super(QobuzTagProduct, self).__init__(Core, json)
        self.set_valid_tags(['id', 'artist_name', 'genre', 'description',
                            'image_large', 'image_small', 'image_thumbnail', 
                            'label', 'price', 'realease_date', 'relevancy', 
                            'title', 'type', 'url'])
        self.__tracks__ = None
        if json:
            self.parse_json(json)

        
    def get_tracks(self):
        return self.__tracks__
    
    def getXbmcItem(self):
        i = super(QobuzTagProduct, self).getXbmcItem()
        i.setLabel(self.getArtist() + ' - ' + self.getTitle() + ' [' + self.getGenre() + ']')
        return i
    
    def parse_json(self, p):
        print p
        self.set('id', p['id'])
        self.set('artist', p['artist'])
        # fixme artist_id or ['artist']['id']?

        # self.set('artist_id', p['artist']['id'])
        self.set('genre', p['genre'])
        self.set('image_large', p['image']['large'])
        self.set('image_large', p['image']['small'])
        self.set('image_small', p['image']['thumbnail'])
        self.set('label', p['label'])
        self.set('price', p['price'])
        self.set('release_date', p['release_date'])
        try:
            self.set('relevancy', p['relevancy'])
        except: pass
        self.set('title', p['title'])
        try:
            self.set('type', p['type'])
        except: pass
        self.set('url', p['url'])
        if not 'tracks' in p:
            return
        if len(p['tracks']) > 0:
            self.__tracks__ = []
            for t in p['tracks']:
                image = ''
                try:
                    image = t['image']['large']
                except:
                    t['image'] = {}
                    t['image']['large'] = p['image']['large']
                release_date = ''
                try:
                    release_date = t['release_date']
                except:
                    t['release_date'] = p['release_date']
                try:
                      genre = t['release_date']
                except:
                    t['genre'] = p['genre']
                print t   
                self.__tracks__.append(QobuzTagTrack(self.Core, t, self))
            else:
                warn(self, "NO TRACK FOR THIS PRODUCT (parse error)")
        self._is_loaded = True
        

'''
'''
class QobuzTagTrack(IQobuzTag):
    
    def __init__(self, Core, json, parent = None):
        super(QobuzTagTrack, self).__init__(Core, json)
        self.set_valid_tags(['playlist_track_id', 'position', 'id', 'title', 
                             'interpreter_name', 'interpreter_id', 
                             'composer_name', 'composer_id',
                             'track_number', 'media_number', 'duration',
                             'created_at', 'streaming_type'])
        #self.json = None
        self.__album = None
        self.parent = None
        if json:
            self.parse_json(json)
    
    def getXbmcItem(self, context = 'album'):
        i = super(QobuzTagTrack, self).getXbmcItem()
        album_title = ''
        try:
            album_title = self.get_album().getTitle()
        except:
            pass
        label = ''
        if context == 'album':
            label = str(self.getTracknumber()) + ' - ' + self.getArtist() + ' - '  + self.getTitle()
        elif context == 'playlist': 
            label = self.getArtist() + ' - ' + self.getTitle()
        elif context == 'songs': 
            label = album_title + ' - ' + self.getArtist() + ' - ' + self.getTitle()
        else:
            raise "Unknown display context"
        i.setProperty('mimetype','audio/flac')
        
        i.setProperty('album', self.getTitle())
        try:
            i.setProperty('genre', self.parent.getGenre())
        except: pass
        i.setProperty('artist', self.getArtist())
        print "Streamtype: " + self.getStreamingType()
        #pprint.pprint(self._json)
        i.setProperty('year', str(self.getYear()))
        if self.getStreamingType() != 'full':
            i.setProperty("IsPlayable",'false')
            i.setProperty('Music', 'true')
            label = '[COLOR=FF555555]' + label + '[/COLOR] [[COLOR=55FF0000]Sample[/COLOR]]'
        else:
            i.setProperty('Music','true')
            i.setProperty("IsPlayable",'false')
        i.setLabel(label)
        # add context menu items (for artist search)
        albumfromthisartist='ActivateWindow(MusicFiles,'+sys.argv[0]+"?id="+self.getArtistId()+"&mode="+str(MODE_ARTIST) + ')'
        # can't use __language__ here... we have lost artistid also.
        #albumfromthisartist='RunScript(plugin.audio.qobuz,'+str(self.Core.Bootstrap.__handle__)+','+self.getArtistId()+','+str(MODE_ARTIST) + ')' 
        menuItems = []
        # action='ActivateWindow(MusicFiles, '+sys.argv[0]+"?mode="+str(MODE_ALBUM)+"&id="+str(t.get_album().id)+')'
        i.addContextMenuItems([('Show albums from this artist', albumfromthisartist)], False)
        #i.addContextMenuItems(menuItems, replaceItems=False)
        
        return i
    
    def get_album(self):
        return self.__album
    
    def getGenre(self):
        genre = ''
        try:
            genre = self.parent.genre
        except: return super(QobuzTagTrack, self).getGenre()
        return genre
    def getLabel(self):
        label = []
        label.append(self.track_number)
        label.append(' - ')
        label.append(self.getArtist())
        label.append(' - ')
        label.append(self.title)
        return ''.join(label)
    
    def parse_json(self, p):
        try:
            self.parse_json(p['info'])
        except: pass
        try:
            self.set('id', p['id'])
        except: pass
        try:
            self.set('playlist_track_id', p['playlist_track_id'])
        except: pass
        try:
            self.set('title', p['title'])
        except: pass
        try:
            self.set('interpreter_name', p['interpreter']['name'])
            self.set('interpreter_id', p['interpreter']['id'])
        except: pass
        try:
            self.set('composer_id', p['composer_id'])
            self.set('composer_name', p['composer_name'])
        except: pass
        try:
            self.set('image_large', p['image']['large'])
        except:
            warn(self, "No image|large for this track")
        try:
            self.set('position', p['position'])
        except: pass
        try:
            self.set('track_number', p['track_number'])
        except: pass
        try:
            self.set('media_number', p['media_number'])
        except: pass
        try:
            self.set('duration', p['duration'])
        except: pass
        try:
            self.set('created_at', p['created_at'])
        except: pass
        try: 
            self.set('streaming_type', p['streaming_type'])
        except: pass
        try:
            self.__album = QobuzTagAlbum(self.Core, p['album'])
        except: 
            warn(self, "NO ALBUM FOR THIS TRACK (Parse error!!!)")
        self._is_loaded = True

'''
'''
class QobuzTagPlaylist(IQobuzTag):
    
    def __init__(self, Core, json):
        super(QobuzTagPlaylist, self).__init__(Core, json)
        self.set_valid_tags([])
        self.__user_playlist = None
        self.__tracks__ = []
        if json:
            self.parse_json(json)
    
    def get_user_playlist(self):
        return self.__user_playlist
    
    def get_tracks(self):
        return self.__tracks__
    
    def parse_json(self, p):
        self.__user_playlist = QobuzTagUserPlaylist(self.Core, p)
        for track in p['tracks']:
            self.__tracks__.append(QobuzTagTrack(self.Core, track))
        self._is_loaded = True
        
