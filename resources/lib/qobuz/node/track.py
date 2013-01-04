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
import xbmcgui

import qobuz
from constants import Mode
from flag import NodeFlag as Flag
from inode import INode
from debug import warn
from gui.util import color, lang, getImage, runPlugin

'''
    NODE TRACK
'''


class Node_track(INode):

    def __init__(self, parent=None, parameters=None):
        super(Node_track, self).__init__(parent, parameters)
        self.type = Flag.TRACK
        self.content_type = 'songs'
        self.qobuz_context_type = 'playlist'
        self.is_folder = False
        self.status = None
        self.image = getImage('song')

    def pre_build_down(self, Dir, lvl = 1, flag = Flag.STOPBUILD):
        if flag & Flag.STOPBUILD == Flag.STOPBUILD:
            return False
        data = qobuz.registry.get(name='track', id=self.id)
        if not data:
            return False
        self.data = data['data']
        if not self.data:
            return False
        return True
    
    def _build_down(self, Dir, lvl, flag=Flag.STOPBUILD):
        Dir.add_node(self)
        return True

    def make_url(self, **ka):
        if not 'mode' in ka: 
            ka['mode'] = Mode.PLAY 
        return super(Node_track, self).make_url(**ka)

    def get_label(self, sFormat="%a - %t"):
        sFormat = sFormat.replace("%a", self.get_artist())
        sFormat = sFormat.replace("%t", self.get_title())
        sFormat = sFormat.replace("%A", self.get_album())
        sFormat = sFormat.replace("%n", str(self.get_track_number()))
        sFormat = sFormat.replace("%g", self.get_genre())
        return sFormat

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
        if album:
            return album
        if not self.parent:
            return ''
        if self.parent.get_type() & Flag.PRODUCT:
            return self.parent.get_title()
        return ''

    def get_image(self):
        try:
            image = self.get_property(('album', 'image', 'large'))
        except:
            pass
        if image:
            return image.replace('_230.', '_600.')
        if not self.parent:
            return self.image
        if self.parent.get_type() & (Flag.PRODUCT | Flag.PLAYLIST):
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

        if genre:
            return genre
        if not self.parent:
            return ''
        if self.parent.get_type() & Flag.PRODUCT:
            return self.parent.get_genre()
        return ''

    def get_streaming_url(self):
        nid = self.id or self.parameters['nid']
        data = qobuz.registry.get(name='user-stream-url', id=nid)
        if not data:
            return ''
        return data['data']['url']

    def get_artist(self):
        s = self.get_property(('artist', 'name'))
        if s:
            return s
        s = self.get_property(('composer', 'name'))
        if s:
            return s
        s = self.get_property(('performer', 'name'))
        if s:
            return s
        s = self.get_property(('interpreter', 'name'))
        if s:
            return s
        s = self.get_property(('composer', 'name'))
        if s:
            return s
        s = self.get_property(('album', 'artist', 'name'))
        if s:
            return s
        return ''

    def get_artist_id(self):
        s = self.get_property(('artist', 'id'))
        if s:
            return int(s)
        s = self.get_property(('composer', 'id'))
        if s:
            return int(s)
        s = self.get_property(('performer', 'id'))
        if s:
            return int(s)
        s = self.get_property(('interpreter', 'id'))
        if s:
            return int(s)
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
            if not date and self.parent and self.parent.get_type() & Flag.PRODUCT:
                return self.parent.get_year()
        except:
            pass
        year = 0
        try:
            year = time.strftime("%Y", time.localtime(date))
        except:
            pass

        return year

    def get_description(self):
        if self.parent:
            return self.parent.get_description()
        return ''

    def is_sample(self):
        nid = self.id or self.parameters['nid']
        data = qobuz.registry.get(name='user-stream-url', id=nid)
        if not data:
            warn(self, "Cannot get stream type for track (network problem?)")
            return ''
        try:
            return data['data']['sample']
        except:
            return ''

    def get_mimetype(self):
        nid = self.id or self.parameters['nid']
        data = qobuz.registry.get(name='user-stream-url', id=nid)
        formatId = None
        if not data:
            warn(self, "Cannot get mime/type for track (network problem?)")
            return ''
        try:
            formatId = int(data['data']['format_id'])
        except:
            warn(self, "Cannot get mime/type for track (restricted track?)")
            return ''
        mime = ''
        if formatId == 6:
            mime = 'audio/flac'
        elif formatId == 5:
            mime = 'audio/mpeg'
        else:
            warn(self, "Unknow format " + str(formatId))
            mime = 'audio/mpeg'
        return mime
    
    """ We add this information only when playing item because it require
        use to fetch data from Qobuz
    """
    def item_add_playing_property(self, item):
        item.setProperty('mimetype', self.get_mimetype())
        item.setPath(self.get_streaming_url())
    
    def makeListItem(self):
        media_number = self.get_media_number()
        if not media_number:
            media_number = 1
        else:
            media_number = int(media_number)
        duration = self.get_duration()
        label = self.get_label()
        isplayable = 'true'

        # Disable free account checking here, purchased track are
        # still playable even with free account, but we don't know yet.
        # if qobuz.gui.is_free_account():
        #    duration = 60
        # label = '[COLOR=FF555555]' + label + '[/COLOR]
        # [[COLOR=55FF0000]Sample[/COLOR]]'

        mode = Mode.PLAY
        url = self.make_url(mode=mode)
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
        if not track_number:
            track_number = 0
        else:
            track_number = int(track_number)
        mlabel = self.get_property(('label', 'name'))
        description = self.get_description()
        comment = ''
        if mlabel:
            comment = mlabel
        if description:
            comment += ' - ' + description
        item.setInfo(type='music', infoLabels={
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
        menuItems = []
        self.attach_context_menu(item, menuItems)
        if len(menuItems) > 0:
            item.addContextMenuItems(menuItems, replaceItems=False)
        return item

    def attach_context_menu(self, item, menuItems=[]):
        colorItem = qobuz.addon.getSetting('color_item')
        if self.parent and self.parent.type & Flag.PLAYLIST:
            url = self.parent.make_url(
                query=str(self.get_property('playlist_track_id'))
            )
            menuItems.append((color(colorItem, lang(
                30073)) + self.get_label(), runPlugin(url)))

        if self.parent and self.parent.type & Flag.FAVORITES:
            ''' REMOVE '''
            url = self.make_url(mode=Mode.FAVORITE_DELETE)
            menuItems.append((color(colorItem, 'Remove from favorite')
                             + self.label, "XBMC.RunPlugin(" + url + ")"))

        ''' Calling base class '''
        super(Node_track, self).attach_context_menu(item, menuItems)
