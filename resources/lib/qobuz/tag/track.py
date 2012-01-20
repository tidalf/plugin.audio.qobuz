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
from tag.album import TagAlbum
from tag.interpreter import TagInterpreter
from tag.composer import TagComposer
from tag.image import TagImage

class TagTrack(ITag):
    
    def __init__(self, json, parent = None):
        super(TagTrack, self).__init__(json, parent)
        self.set_valid_tags(['playlist_track_id', 'position', 'id', 'title', 
                             'track_number', 'media_number', 'duration',
                             'created_at', 'streaming_type'])
        if json: self.parse_json(json)

    def getLabel(self):
        label = []
        label.append(self.track_number)
        label.append(' - ')
        label.append(self.getArtist())
        label.append(' - ')
        label.append(self.title)
        return ''.join(label)

    def parse_json(self, p):
        self.auto_parse_json(p)
        if 'album' in p:
            data = TagAlbum(p['album'])
            self.add_child( data )
        if 'interpreter' in p:
            data = TagInterpreter(p['interpreter'])
            self.add_child( data )
        if 'composer' in p:
            data = TagComposer(p['composer'])
            self.add_child( data )
        if 'image' in p:
            data = TagImage(p['image'])
            self.add_child( data )
        self._is_loaded = True

    def getDuration(self, sep = 0):
        try:
            (sh,sm,ss) = self.duration.split(':')
        except: return 0
        return (int(sh) * 3600 + int(sm) * 60 + int(ss))

    def getTrackNumber(self, sep = ''):
        try: return int(self.track_number)
        except: return 0

    def getTitle(self, sep = ''):
        try: return self.title
        except: return ''

    def getArtist(self, sep = ''):
        artist = ''
        artist = self.getInterpreter()
        if artist: return artist
        artist = self.getComposer()
        if artist: return artist
        parent = self.get_parent()
        if parent:
            artist = parent.getArtist()
        return artist
    
    def getAlbum(self, sep = ''):
        album = super(TagTrack, self).getAlbum(sep)
        parent = self.get_parent()
        if not album and parent:
            try: album = parent.title
            except: pass
        return album

    def getAlbumId(self, sep = ''):
        albumid = super(QobuzTagTrack, self).getAlbumId(sep)
        parent = self.get_parent()
        if not albumid and parent:
            albumid = parent.id
        return albumid

    def getStreamingType(self, sep = ''):
        try: return self.streaming_type
        except: return ''        
    
    def _getDate(self):
        parent = self.get_parent()
        date = None
        if parent: date = parent.getDate()
        else: date = self.getDate()
        return date
    
    def getYear(self):
        date = self._getDate()
        year = 0
        if not date: return year
        try: year = int(date.split('-')[0])
        except: pass
        return year
        
    def getXbmcItem(self, context = 'album', pos = 0, fanArt = 'fanArt'):
        import xbmcgui
        import qobuz
        parent = self.get_parent()
        album = self.getAlbum()
        artist = self.getArtist()
        track_number = self.getTrackNumber()
        media_number = 0
        try:
            media_number = int(self.media_number)
        except: pass
#        if media_number > 1:
#            qobuz.gui.set_sort_enabled(False)
#            
        if media_number == 0: media_number = 1
        track_number = media_number * 100 + track_number
        
        genre = ''
        try: genre = parent.getGenre()
        except: genre = self.getGenre()
            
        image = self.getImage()  
        if not image and parent: 
            image = parent.getImage()

        title = self.getTitle()
        duration = self.getDuration()
        label = ''
        if context == 'album':
            label = str(track_number) + ' - ' + artist + ' - '  + title
        elif context == 'playlist': 
            label = artist + ' - ' + title
        elif context == 'songs': 
            label = album + ' - ' + artist + ' - ' + title
        elif context == 'player':
            label = str(track_number) + ' - ' + artist + ' - '  + title
        else:
            raise "Unknown display context"
    
        if self.getStreamingType() != 'full':
            label =  '[COLOR=FF555555]' + label + '[/COLOR] [[COLOR=55FF0000]Sample[/COLOR]]'
            duration = 60
#        if not qobuz.api.auf:
#            duration = 60
        i = xbmcgui.ListItem(label, label, image, image)
        if fanArt:
            i.setProperty('fanart_image', qobuz.image.access.get(fanArt))
        i.setProperty('title', label)
        i.setLabel(label)
        i.setLabel2(str(media_number) + ' - ' + str(track_number) + ' - ' + album + ' - ' + artist + ' - ' + title)
        i.setInfo(type = 'music',
                  infoLabels = {'count': pos,
                                #'songid': str(self.id),
                                'title': title,
                                'artist': artist,
                                'genre': genre,
                                'tracknumber': track_number,
                                'discnumber': str(media_number),
                                'filename': i.getLabel2(),
                                'album': album,
                                'duration': duration,
                                'year': self.getYear(),
                                'comment': 'Qobuz Music Streaming Service'
                                })
        i.setProperty('DiscNumber', str(media_number))
        i.setProperty('IsPlayable', 'true')
        i.setProperty('Music', 'true')
        i.setProperty('IsInternetStream', 'false')
        i.setThumbnailImage(image)
        i.setIconImage(image)
        i.setProperty('image', image)
        qobuz.gui.setContextMenu(i)
        return i
