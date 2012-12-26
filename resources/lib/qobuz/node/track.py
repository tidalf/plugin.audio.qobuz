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

import xbmcgui

import qobuz
from constants import Mode
from flag import NodeFlag
from node import Node

from debug import error, debug, warn

'''
    NODE TRACK
'''

class Node_track(Node):

    def __init__(self, parent = None, parameters = None):
        super(Node_track, self).__init__(parent, parameters)
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_TRACK
        self.set_content_type('songs')
        self.qobuz_context_type = 'playlist'
        self.set_is_folder(False)
        self.status = None

    def _build_down(self, xbmc_directory, lvl, flag = None):
        if flag & NodeFlag.DONTFETCHTRACK:
            return False
        else:
            #self.set_cache(xbmc_directory.Progress)
            nid = self.get_parameter('nid')
            self.set_data(qobuz.registry.get(name='track', id=nid)['data'])
            xbmc_directory.add_node(self)
            return True

    def set_cache(self, progress = None):
        id = self.get_id()
        if not id:
            try:
                id = self.get_parameter('nid')
            except: pass
        if not id:
            error(self, "Cannot set cache without id")
            return False
        return True

    def make_url(self, mode = Mode.PLAY):
        return super(Node_track, self).make_url(mode)

    def get_label(self, format = "%a - %t"):
        format = format.replace("%a", self.get_artist())
        format = format.replace("%t", self.get_title())
        try:
            format = format.replace("%A", self.get_album()) # .encode('utf8', 'ignore'))
        except: pass
        format = format.replace("%n", str(self.get_track_number()))
        format = format.replace("%g", self.get_genre()) # .encode('utf8', 'ignore'))
        return format

    def get_composer(self):
        try: 
            return self.get_property(('composer', 'name'))
        except:
            return -1
        
    def get_interpreter(self):
        try: 
            return self.get_property(('performer', 'name'))
        except: 
            return -1
        
    def get_album(self):
        try: 
            album = self.get_property(('album', 'title'))
        except:
            return -1
        if album: return album
        if not self.parent: return ''
        if self.parent.get_type() & NodeFlag.TYPE_PRODUCT:
            return self.parent.get_title()
        return ''

    def get_image(self):
        try:
            image = self.get_property(('album', 'image', 'large'))
        except: pass
        if image: return image.replace('_230.', '_600.')
        if not self.parent: return ''
        if self.parent.get_type() & (NodeFlag.TYPE_PRODUCT | NodeFlag.TYPE_PLAYLIST):
            return self.parent.get_image()

    def get_playlist_track_id(self):
        return self.get_property(('playlist_track_id'))

    def get_position(self):
        return self.get_property(('position'))

    def get_title(self):
        return self.get_property('title')

    def get_genre(self):
        try:
            genre = self.get_property(('album', 'genre', 'name'))
        except:
            genre = "none"
        
        if genre: return genre
        if not self.parent: return ''
        if self.parent.get_type() & NodeFlag.TYPE_PRODUCT:
            return self.parent.get_genre()
        return ''

    def get_streaming_url(self):
        nid = self.get_id() or self.parameters['nid']
        data = qobuz.registry.get(name='stream-url', id=nid)
        if not data: return None
        return data['data']['url']

    def get_artist(self):
        s = self.get_interpreter()
        if s: return s
        return self.get_composer()

    def get_artist_id(self):
        s = self.get_property(('artist', 'id'))
        if s: return int(s)
        s = self.get_property(('composer', 'id'))
        if s: return int(s)
        s = self.get_property(('performer', 'id'))
        if s: return int(s)
        s = self.get_property(('interpreter', 'id'))
        if s: return int(s)
        return None

    def get_track_number(self):
        return self.get_property(('track_number'))

    def get_media_number(self):
        return self.get_property(('media_number'))

    def get_duration(self):
        duration = self.get_property(('duration'))
        if duration:
            return duration
        else: 
            return -1

    def get_year(self):
        import time
        try:
            date = self.get_property(('album', 'released_at'))
            if not date and self.parent and self.parent.get_type() & NodeFlag.TYPE_PRODUCT:
                return self.parent.get_year()
        except: pass
        year = 0
        try: year = time.strftime("%Y", time.localtime(date))
        except: pass
        
        return year

    def  get_description(self):
        if self.parent: return self.parent.get_description()
        return ''


    def is_sample(self):
        nid = self.get_id() or self.parameters['nid']
        data = qobuz.registry.get(name='stream-url', id=nid)
        if not data:
            warn(self, "Cannot get stream type for track (network problem?)")
            return ''
        try: 
            return data['data']['sample']
        except: 
            return ''
    
    def get_mimetype(self):
        nid = self.get_id() or self.parameters['nid']
        data = qobuz.registry.get(name='stream-url', id=nid)
        if not data:
            warn(self, "Cannot get mime/type for track (network problem?)")
            return ''
        try: 
            format = int(data['data']['format_id'])
        except:
            warn(self, "Cannot get mime/type for track (restricted track?)")
            return ''
        mime = ''
        if format == 6:
            mime = 'audio/flac'
        elif format == 5:
            mime = 'audio/mpeg'
        else:
            warn(self, "Unknow format " + str(format))
            mime = 'audio/mpeg'
        return mime

    def make_XbmcListItem(self):
        media_number = self.get_media_number()
        if not media_number: media_number = 1
        else: media_number = int(media_number)
        duration = self.get_duration()
        label = self.get_label()
        isplayable = 'true'
        
        # Disable free account checking here, purchased track are still playable even with free account, but we don't know yet.
        #if qobuz.gui.is_free_account():
        #    duration = 60
        #    label = '[COLOR=FF555555]' + label + '[/COLOR] [[COLOR=55FF0000]Sample[/COLOR]]'
        
        mode = Mode.PLAY
        url = self.make_url(mode)
        item = xbmcgui.ListItem(label,
                                label,
                                str(self.get_image()),
                                str(self.get_image()),
                                url)
        if not item:
            warn(self, "Cannot create xbmc list item")
            return None
        item.setPath(url)
        track_number = self.get_track_number()
        if not track_number: track_number = 0
        else: track_number = int(track_number)
        mlabel = self.get_property(('label', 'name'))
        description = self.get_description()
        comment = ''
        if mlabel: comment = mlabel
        if description: comment += ' - ' + description
        item.setInfo(type = 'music', infoLabels = {
                                   #'track_id': self.get_id(),
                                   'title': self.get_title(),
                                   'album': self.get_album(),
                                   'genre': self.get_genre(),
                                   'artist': self.get_artist(),
                                   'tracknumber': track_number,
                                   'duration': duration,
                                   'year': self.get_year(),
                                   'comment': comment
                                   })
        item.setProperty('discnumber', str(media_number))
        item.setProperty('IsPlayable', isplayable)
        item.setProperty('IsInternetStream', isplayable)
        item.setProperty('Music', isplayable)
        self.attach_context_menu(item)
        return item

    def hook_attach_context_menu(self, item, menuItems):
        color = qobuz.addon.getSetting('color_item')
        if self.parent and self.parent.type & NodeFlag.TYPE_PLAYLIST:
            url = self.parent.make_url(Mode.PLAYLIST_REMOVE_TRACK) + '&track-id=' + str(self.get_property('playlist_track_id'))
            menuItems.append((qobuz.utils.color(color, qobuz.lang(30073)) + self.get_label(), 'XBMC.RunPlugin("%s")' % (url)))
