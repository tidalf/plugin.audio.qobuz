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
from constants import *
from flag import NodeFlag
from node import node

from node_userplaylists import node_userplaylists
'''
    NODE TRACK
'''
from data.track import QobuzTrack
from tag.track import TagTrack

class node_root(node):
    
    def __init__(self, parent = None):
        super(node_root, self).__init__(parent)
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_ROOT
        
    def _build_down(self, lvl, flag = None):
        pass
        
    def _get_xbmc_items(self, list, lvl, flag):
        print "Return root content"
        url = sys.argv[0] + '/?mode=' + str(MODE_NODE) + '&nt=' + str(NodeFlag.TYPE_USERPLAYLISTS)
        item = xbmcgui.ListItem('Playlist', '', '', '', url)
        list.append((url, item, True))
        url = sys.argv[0] + '/?mode=' + str(MODE_NODE) + '&nt=' + str(NodeFlag.TYPE_RECOMMANDATION)
        item = xbmcgui.ListItem('Recos', '', '', '', url)
        list.append((url, item, True))