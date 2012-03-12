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
import pprint
import qobuz
from constants import Mode
from flag import NodeFlag
from node import Node
from cache.track import Cache_track
from cache.track_stream_url import Cache_track_stream_url
from debug import info, warn, error
#from gettext import re
'''
    NODE TRACK
'''

class Node_track(Node):

    def __init__(self, parent = None, parameters = None):
        super(Node_track, self).__init__(parent, parameters)
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_TRACK
        self.set_content_type('songs')
        self.set_is_folder(False)
        self.cache = None
        self.cache_url = None

    def _build_down(self, lvl, flag = None):
        self._set_cache()
        if flag & NodeFlag.DONTFETCHTRACK:
            print "Don't download track data"
        else:    
            self.set_data(self.cache.get_data())
        return False

    def _get_xbmc_items(self, list, lvl, flag):
        print "RETURN XBMC ITEM: TRACK"
        mode = Mode.PLAY
        list.append((self.make_url(mode), self.make_XbmcListItem(), self.is_folder()))
        return list

    def _set_cache(self):
        id = self.get_id()
        #print "ID: " + str(id )
        if not id:
            try:
                id = self.get_parameter('nid')
            except: pass
        if not id:
            error(self, "Cannot set cache without id")
            return False
        self.set_id(id)
        self.cache = Cache_track(id, 'playlist', False)
        return True
    
    def make_url(self, mode = Mode.PLAY):
        return super(Node_track, self).make_url(mode)
    
    def get_label(self, format = "%a - %t"):
        format = format.replace("%a", self.get_artist())
        format = format.replace("%t", self.get_title())
        format = format.replace("%A", self.get_album())
        format = format.replace("%n", self.get_track_number())
        format = format.replace("%g", self.get_genre())
        return format

    def get_composer(self):
        return self.get_property(('composer', 'name'))

    def get_interpreter(self):
        return self.get_property(('interpreter', 'name'))

    def get_album(self):
        album = self.get_property(('album', 'title'))
        if album: return album
        if not self.parent: return ''
        if self.parent.get_type() & NodeFlag.TYPE_PRODUCT:
            return self.parent.get_title()
            
    def get_image(self):
        image = self.get_property(('album', 'image', 'large'))
        if image: return image.replace('_230.jpg', '_600.jpg')
        if not self.parent: return ''
        if self.parent.get_type() & NodeFlag.TYPE_PRODUCT:
            return self.parent.get_image()

    def get_playlist_track_id(self):
        return self.get_property(('playlist_track_id'))

    def get_streaming_type(self):
        return self.get_property(('streaming_type'))

    def get_position(self):
        return self.get_property(('position'))

    def get_title(self):
        return self.get_property('title')

    def get_genre(self):
        genre = self.get_property(('album', 'genre', 'name'))
        if genre: return genre
        if not self.parent: return ''
        if self.parent.get_type() & NodeFlag.TYPE_PRODUCT:
            return self.parent.get_genre()

    def get_artist(self):
        s = self.get_interpreter()
        if s: return s
        return self.get_composer()

    def get_artist_id(self):
        s = self.get_property(('artist', 'id'))
        if s: return s
        s =  self.get_property(('composer', 'id'))
        if s: return s
        s =  self.get_property(('interpreter', 'id'))
        return s

    def get_track_number(self):
        return self.get_property(('track_number'))

    def get_media_number(self):
        return self.get_property(('media_number'))

    def get_duration(self):
        duration = self.get_property(('duration'))
        if duration:
            (sh, sm, ss) = duration.strip().split(':')
            return (int(sh) * 3600 + int(sm) * 60 + int(ss))
        return -1

    def get_year(self):
        date = self.get_property(('album', 'release_date'))
        if not date and self.parent and self.parent.get_type() & NodeFlag.TYPE_PRODUCT:
            return self.parent.get_year()
        year = 0
        try: year = int(date.split('-')[0])
        except: pass
        return year

    def  get_description(self):
        if self.parent: return self.parent.get_description()
        return ''
    
    def _set_cache_streaming_url(self):
        if not self.cache_url:
            self.cache_url = Cache_track_stream_url(self.get_id())
        self.cache_url.fetch_data()
        
        
    def get_streaming_url(self):
        self._set_cache_streaming_url()
        data = self.cache_url.get_data()
        print repr(data)
        return data['streaming_url']
    
    def get_mimetype(self):
        self._set_cache_streaming_url()
        data = self.cache_url.get_data()
        format = int(data['format_id'])
        mime = ''
        if format == 6:
            mime = 'audio/flac'
        else:
            mime = 'audio/mpeg'
        return mime
        
    def make_XbmcListItem(self):
        import xbmcgui

#        print repr(self.get_data())
#        print "URL: " + self.get_url()
#        print "Label: " + self.get_label()
#        print repr(self._data)

        media_number = self.get_media_number()
        if not media_number: media_number = 1
        else: media_number = int(media_number)
        
        duration = self.get_duration()
        label = self.get_label()
        if self.get_streaming_type() == 'sample':
            duration = 60
            label =  '[COLOR=FF555555]' + label + '[/COLOR] [[COLOR=55FF0000]Sample[/COLOR]]'
            
        mode = Mode.PLAY
        url = self.get_url(mode)
        #print "TRACK url: " + url
        item = xbmcgui.ListItem(label,
                                label,
                                self.get_image(),
                                self.get_image(),
                                url)
        item.setPath(url)                        
        track_number = self.get_track_number()
        if not track_number: track_number = 0
        else: track_number = int(track_number)
        
        item.setInfo(type = 'music', infoLabels = {
                                   'track_id': self.get_id(),
                                   'title': self.get_title(),
                                   'album': self.get_album(),
                                   'genre': self.get_genre(),
                                   'artist': self.get_artist(),
                                   'tracknumber': track_number,
                                   'discnumber': media_number,
                                   'duration': duration,
                                   'year': self.get_year(),
                                   'comment': self.get_description()
                                   })
        item.setProperty('node_id', self.get_id())
        item.setProperty('IsPlayable', 'true')
        item.setProperty('IsInternetStream', 'true')
        item.setProperty('Music', 'true')
        #print "URL: " + repr(self.get_url())
        return item

    def hook_attach_context_menu(self, item, node, menuItems, color):
        pass
#        args = 'mode=%i&nt=%i&nid=%d' % (Mode.VIEW, 
#                                         NodeFlag.TYPE_PLAYLIST, 
#                                         self.get_property(('album', 'id'))
#                                         )
#        print "ARGS: " + args
#        cmd = 'RunScript("%s", "%s")' % (sys.argv[0], args)
#        print "CMD: " + cmd
#        menuItems.append(("View Album", cmd))
