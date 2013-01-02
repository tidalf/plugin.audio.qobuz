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
from flag import NodeFlag as Flag
from node import Node
from friend import Node_friend
from debug import info, warn
from gui.util import color, getImage, runPlugin

'''
    NODE FRIEND
'''
from track import Node_track


class Node_friend_list(Node):

    def __init__(self, parent=None, parameters=None, progress=None):
        super(Node_friend_list, self).__init__(parent, parameters)
        self.type = Flag.NODE | Flag.FRIEND_LIST
        self.name = self.get_parameter('name')
        self.image = getImage('artist')
        self.label = str(self.name) + "'s Friends (i8n)" if (
            self.name) else "Friends (i8n)"
        self.label2 = ""
        self.url = None
        self.is_folder = True
        self.content_type = 'artist'

    def make_url(self, **ka):
        url = super(Node_friend_list, self).make_url(**ka)
        if self.name:
            url += "&name=" + self.name
        return url

    def _build_down(self, xbmc_directory, lvl, flag=None):
        info(self, "Build-down friends list " + repr(self.name))
        if self.name:
            data = qobuz.registry.get(
                name='user-playlists', id=self.name, limit=0)
        else:
            data = qobuz.registry.get(name='user-playlists', limit=0)
        if not data:
            warn(self, "No friend data")
            return False
        # extract all owner names from the list
        friend_list = []
        for item in data['data']['playlists']['items']:
            friend_list.append(item['owner']['name'])
        # add previously stored
        if (not self.name):
            data = qobuz.registry.get(
                name='user')['data']['user']['player_settings']
            for name in data['friends']:
                friend_list.append(str(name))
        # remove duplicates
        keys = {}
        for e in friend_list:
            keys[e] = 1
        friend_list = keys.keys()
        # and add them to the directory
        for name in friend_list:
            node = Node_friend(None, {'name': str(name)})
            self.add_child(node)

    def attach_context_menu(self, item, menuItems=[]):
        colorItem = qobuz.addon.getSetting('color_item')
        # color_warn = qobuz.addon.getSetting('color_item_caution')
        label = self.get_label()

        url = self.make_url(type=Flag.FRIEND, nm='create')
        menuItems.append((color(
            colorItem, 'Add friend (i8n)' + ': ') + label, runPlugin(url)))

        ''' Calling base class '''
        super(Node_friend_list, self).attach_context_menu(item, menuItems)
