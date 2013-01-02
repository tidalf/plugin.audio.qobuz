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
from flag import NodeFlag
from node import Node
from track import Node_track
from product import Node_product
from debug import warn
from gui.util import lang, color
import weakref

'''
    NODE Artist
'''


class Node_artist(Node):

    def __init__(self, parent=None, parameters=None, progress=None):
        super(Node_artist, self).__init__(parent, parameters)
        self.type = NodeFlag.NODE | NodeFlag.ARTIST
        self.set_label(self.get_name())
        self.is_folder = True
        self.slug = ''
        self.content_type = 'artist'

    def hook_post_data(self):
        self.name = self.get_property('name')
        self.image = self.get_image()
        self.slug = self.get_property('slug')
        self.label = self.name
        
    def _build_down(self, xbmc_directory, lvl, flag=None):
        colorItem = qobuz.addon.getSetting('color_item')
        print "Building down ARTIST"
        offset = self.get_parameter('offset') or 0
        limit = qobuz.addon.getSetting('pagination_limit')
        data = qobuz.api.artist_get(
            artist_id=self.id, limit=limit, offset=offset, extra='albums')
        self.data = data
        node_artist = Node_artist()
        node_artist.data = self.data
        node_artist.label = '[ %s ]' % (color(colorItem, node_artist.label))
        self.add_child(node_artist)
        if not self.data:
            warn(self, "Build-down: Cannot fetch favorites data")
            return False
        if not 'albums' in data: return True
        for pData in data['albums']['items']:
            node = Node_product()
            node.data = pData
            self.add_child(node)
        warn(self, 'DATA ARTIST: ' + pprint.pformat(data))

        return True

        del self._data['tracks']

    def get_artist_id(self):
        return self.id
    
    def get_image(self):
        image = self.get_property(('image', 'extralarge'))
        if not image: image = self.get_property(('image', 'mega'))
        if not image: image = self.get_property('picture')
        if image: image.replace('34s', '126s')
        if image: return image
        return ''
    
    def get_title(self):
        return self.get_name()
    
    def get_artist(self):
        return self.get_name()
    
    def get_name(self):
        name = self.get_property('name')
        return name

    def get_owner(self):
        return self.get_property(('owner', 'name'))

    def get_description(self):
        return self.get_property('description')

    def make_XbmcListItem(self):
        image = self.get_image()
        url = self.make_url()
        name = self.get_label()
        item = xbmcgui.ListItem(name,
                                name,
                                image,
                                image,
                                url)
        item.setInfo('picture', {
                               'title': self.get_property('slug')
                    })
        if not item:
            warn(self, "Error: Cannot make xbmc list item")
            return None
        item.setPath(url)
        menuItems = []
        self.attach_context_menu(item, menuItems)
        if len(menuItems) > 0:
            item.addContextMenuItems(menuItems, replaceItems=False)
        return item
