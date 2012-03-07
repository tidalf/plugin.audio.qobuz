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
from constants import *
from flag import NodeFlag
from node import node
from debug import info
'''
    NODE VIRTUAL PLAYLIST
'''
from data.virtual_playlist import cache_virtual_playlist
from tag.playlist import TagPlaylist
from tag.track import TagTrack
from node_track import node_track

class node_virtual_playlist(node):

    def __init__(self, parent = None, parameters = None):
        super(node_virtual_playlist, self).__init__(parent, parameters)
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_VIRTUAL_PLAYLIST

    def _build_down(self, lvl, flag = None):
        o = cache_virtual_playlist()
        data = o.get_data()
        o.playlist.set_label('Poom')
        self.set_label(o.playlist.get_label())
        self.set_json(data)
        for track in data['tracks']:
            c = node_track()
            c.set_json(track)
            c.set_id(track['id'])
            c.setLabel(track['title'])
            c.set_url()
            self.add_child(c)
        return True

    def _get_xbmc_items(self, list, lvl, flag):
        for c in self.childs:
            tag = TagTrack(c.get_json())
            item = tag.getXbmcItem()
            list.append((item.getProperty('path'), item, False))
        return True


