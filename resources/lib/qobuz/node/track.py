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

import qobuz
from constants import Mode
from flag import NodeFlag
from node import Node
from cache.track import Cache_track
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

    def _build_down(self, lvl, flag = None):
        if flag & NodeFlag.DONTFETCHTRACK:
            #print "Don't fetch track data"
            return False

    def _get_xbmc_items(self, list, lvl, flag):
        pass

    def _set_cache(self):
        id = self.get_id()
        if not id:
            try:
                id = self.get_parameter('nid')
                print "PLOPPPP: " + str(id)
            except: pass
        if not id:
            error(self, "Cannot set cache without id")
            return False
        self.set_id(id)
        self.cache = Cache_Track(id)
        return True

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
        return self.get_property(('album', 'title'))

    def get_image(self):
        image = self.get_property(('album', 'image', 'large'))
        if image:
            return image.replace('_230.jpg', '_600.jpg')
        return ''

    def get_playlist_track_id(self):
        return self.get_property(('playlist_track_id'))

    def get_streaming_type(self):
        return self.get_property(('streaming_type'))

    def get_position(self):
        return self.get_property(('position'))

    def get_title(self):
        return self.get_property('title')

    def get_genre(self):
        return self.get_property(('album', 'genre', 'name'))

    def get_artist(self):
        s = self.get_interpreter()
        if s: return s
        return self.get_composer()

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
        year = 0
        try: year = int(date.split('-')[0])
        except: pass
        return year


    def make_XbmcListItem(self):
        import xbmcgui
        self.set_url(Mode.PLAY)
#        print repr(self.get_data())
#        print "URL: " + self.get_url()
#        print "Label: " + self.get_label()
#        print repr(self._data)
        item = xbmcgui.ListItem(self.get_label(),
                                self.get_label(),
                                self.get_image(),
                                self.get_image(),
                                self.get_url())
        item.setPath(self.get_url())
        track_number = self.get_track_number()
        if not track_number: track_number = 0
        else: track_number = int(track_number)
        item.setInfo(type = 'music',
                     infoLabels = {
                                   'track_id': self.get_id(),
                                   'title': self.get_title(),
                                   'album': self.get_album(),
                                   'genre': self.get_genre(),
                                   'artist': self.get_artist(),
                                   'tracknumber': track_number,
                                   #'discnumber': self.get_media_number(),
                                   'duration': self.get_duration(),
                                   'year': self.get_year(),
                                   'comment': "Qobuz Music Streaming Service"

                                   })
        item.setProperty('IsPlayable', 'true')
        item.setProperty('IsInternetStream', 'true')
        item.setProperty('Music', 'true')
        #print "URL: " + repr(self.get_url())
        return item
