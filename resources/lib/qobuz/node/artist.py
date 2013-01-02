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
from debug import warn
from gui.util import lang

'''
    NODE PLAYLIST
'''


class Node_artist(Node):

    def __init__(self, parent=None, parameters=None, progress=None):
        super(Node_artist, self).__init__(parent, parameters)
        self.type = NodeFlag.NODE | NodeFlag.FAVORITES
        self.set_label(lang(30079))
        self.is_folder = True

        self.name = lang(30079)
        self.label = lang(30079)

        self.content_type = 'artist'

    def _build_down(self, xbmc_directory, lvl, flag=None):
        data = qobuz.registry.get(name='user-favorites')
        if not data:
            warn(self, "Build-down: Cannot fetch favorites data")
            return False
        self.data = data
        albumseen = {}
        warn(self, pprint.pformat(data))
        for track in data['data']['tracks']['items']:
            node = Node_track()
            node.data = track
            self.add_child(node)

        for product in self.filter_products(data):
            self.add_child(product)
        return True

        del self._data['tracks']

    def get_name(self):
        name = self.get_property('name')
        return name

    def get_owner(self):
        return self.get_property(('owner', 'name'))

    def get_description(self):
        return self.get_property('description')

    def make_XbmcListItem(self):
        image = self.get_image()
        owner = self.get_owner()
        url = self.make_url()
        item = xbmcgui.ListItem(self.label,
                                owner,
                                image,
                                image,
                                url)
        if not item:
            warn(self, "Error: Cannot make xbmc list item")
            return None
        item.setPath(url)
        self.attach_context_menu(item)
        return item
