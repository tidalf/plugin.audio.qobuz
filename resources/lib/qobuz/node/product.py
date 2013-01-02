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
from flag import NodeFlag
from node import Node
from debug import warn
from gui.util import getImage

'''
    NODE PRODUCT
'''

from track import Node_track

SPECIAL_PURCHASES = ['0000020110926', '0000201011300', '0000020120220',
                     '0000020120221']


class Node_product(Node):

    def __init__(self, parent=None, params=None):
        super(Node_product, self).__init__(parent, params)
        self.type = NodeFlag.NODE | NodeFlag.PRODUCT
        self.image = getImage('album')
        self.content_type = 'albums'
        self.is_special_purchase = False
        self.offset = None

    def _build_down(self, xbmc_directory, lvl, flag=None):
        nid = self.id
        data = None
        if self.is_special_purchase:
            data = qobuz.registry.get(name='purchase', id=nid)
        else:
            data = qobuz.registry.get(name='product', id=nid)
        if not data:
            warn(self, "Cannot fetch product data")
            return False
        self.data = data['data']
        tracks = None
        if self.is_special_purchase:
            tracks = self._filter_tracks(data['data'][''])
        else:
            tracks = data
        for track in tracks['data']['tracks']['items']:
            node = Node_track()
            node.data = track
            self.add_child(node)
        self.add_pagination(data['data'])
        return len(tracks['data']['tracks']['items'])

    def _filter_tracks(self, tracks):
        ltracks = []
        id = self.id
        for track in tracks:
            ltracks.append(track)
        return ltracks

    def make_XbmcListItem(self):
        image = self.get_image()
        item = xbmcgui.ListItem(
            label=self.get_label(),
            label2=self.get_label2(),
            iconImage=self.get_image(),
            thumbnailImage=self.get_image(),
            path=self.make_url(),
        )
        item.setInfo('music', infoLabels={
            'genre': self.get_genre(),
            'year': self.get_year(),
            'artist': self.get_artist(),
            'title': self.get_title(),
            'album': self.get_title(),
        })
        menuItems = []
        self.attach_context_menu(item, menuItems)
        if len(menuItems) > 0:
            item.addContextMenuItems(menuItems, replaceItems=False)
        return item

    '''
    PROPERTIES
    '''
    def get_artist(self):
        a = self.get_property(('artist', 'name'))
        if a:
            return a
        a = self.get_property(('interpreter', 'name'))
        if a:
            return a
        a = self.get_property(('composer', 'name'))
        if a:
            return a
        return ''

    def get_album(self):
        album = self.get_property('name')
        if not album:
            return ''
        return album

    def get_artist_id(self):
        a = self.get_property(('artist', 'id'))
        if a:
            return int(a)
        a = self.get_property(('interpreter', 'id'))
        if a:
            return int(a)
        a = self.get_property(('composer', 'id'))
        if a:
            return int(a)
        return ''

    def get_title(self):
        return self.get_property('title')

    def get_image(self):
        image = self.get_property(('image', 'large'))
        if image:
            self.image = image
            return image
        if self.parent:
            image = self.parent.get_image()
            if image:
                self.image = image
        image = self.image.replace('_230.', '_600.')
        return self.image

    def get_label(self):
        try:
            label = ''.join((self.get_artist(), ' - ', self.get_title()))
        except:
            label = self.get_title()
        return label

    def get_label2(self):
        return self.get_label()

    def get_genre(self):
        return self.get_property(('genre', 'name'))

    def get_year(self):
        import time
        date = self.get_property(('released_at'))
        if not date:
            date = self.get_property(('released_at'))
        year = 0
        try:
            year = time.strftime("%Y", time.localtime(date))
        except:
            pass
        return year

    def get_description(self):
        description = self.get_property('description')
        if description:
            return description
        return self.get_property(('data', 'description'))
