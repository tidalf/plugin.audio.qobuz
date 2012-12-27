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
from friend import Node_friend
from debug import info, warn, error

'''
    NODE FRIEND
'''
from track import Node_track

class Node_friend_list(Node):

    def __init__(self, parent = None, parameters = None, progress = None):
        super(Node_friend_list, self).__init__(parent, parameters)
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_FRIEND_LIST
        self.label = "Friend (i8n)"
        self.label2 = ""
        self.url = None
        self.set_is_folder(True)
        self.content_type = 'artist'
  
    def _build_down(self, xbmc_directory, lvl, flag = None):
        info(self, "Build-down playlist")
        data = qobuz.registry.get(name='user')['data']['user']['player_settings']
        print pprint.pformat(data)
        if not data:
            warn(self, "No friend data")
            return False
        for name in data['friends']:
            print "Friend ID: " + repr(name)
            node = Node_friend()
            node.set_name(str(name))
            self.add_child(node)

    def hook_attach_context_menu(self, item, menuItems):
        color = qobuz.addon.getSetting('color_item')
        color_warn = qobuz.addon.getSetting('color_item_caution')
        label = self.get_label()
        
        ''' SET AS CURRENT '''
        url = self.make_url(Mode.FRIEND_ADD)
        menuItems.append((qobuz.utils.color(color, 'Add friend (i8n)' + ': ') + label, "XBMC.RunPlugin("+url+")"))
