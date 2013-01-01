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
import xbmc

import qobuz
from flag import NodeFlag
from node import Node
from debug import info, warn, error, debug
from gui.util import color, lang, getImage, notifyH, containerRefresh

'''
    NODE USER PLAYLISTS
'''

from playlist import Node_playlist

class Node_user_playlists(Node):

    def __init__(self, parent = None, parameters = None):
        super(Node_user_playlists, self).__init__(parent, parameters)
        self.label = lang(30019)
        self.image = getImage('userplaylists')
        self.label2 = 'Keep your current playlist'
        self.type = NodeFlag.NODE | NodeFlag.USERPLAYLISTS
        self.content_type = 'files'
        display_by = self.get_parameter('display-by')
        if not display_by: display_by = 'songs'
        self.set_display_by(display_by)
        display_cover = qobuz.addon.getSetting('userplaylists_display_cover')
        if display_cover == 'true': display_cover = True
        else: display_cover = False
        self.display_product_cover = display_cover

    def set_display_by(self, type):
        vtype = ('product', 'songs')
        if not type in vtype:
            error(self, "Invalid display by: " + type)
        self.display_by = type

    def get_display_by(self):
        return self.display_by

    def _build_down(self, xbmc_directory, lvl, flag = None):
        login = qobuz.addon.getSetting('username')
        offset = self.get_parameter('offset') or 0
        limit = qobuz.addon.getSetting('pagination_limit')
        debug(self, "Build-down: user playlists")
        data = qobuz.registry.get(name='user-playlists', limit=limit, offset=offset)
        if not data:
            warn(self, "Build-down: Cannot fetch user playlists data")
            return False
        cid = qobuz.registry.get(name='user-current-playlist-id', noRemote=True)
        if cid: cid = int(cid['data'])
        for playlist in data['data']['playlists']['items']:
            node = Node_playlist()
            node.data = playlist
            if self.display_product_cover:
                pass
            if (cid and cid == node.id):
                node.set_is_current(True)
            if node.get_owner() == login:
                node.set_is_my_playlist(True)
            self.add_child(node)
        self.add_pagination(data['data'])
        return True
            

        

    

