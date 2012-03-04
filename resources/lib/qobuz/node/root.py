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
from node import Node
from user_playlists import Node_user_playlists 

'''
    NODE ROOT
    
    Sibling of root are playlist, recos, search, purchases...
'''

class Node_root(Node):
    
    def __init__(self, parent = None, parameters = None):
        super(Node_root, self).__init__(parent, parameters)
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_ROOT
        
    def _build_down(self, lvl, flag = None):
        userplaylists = Node_user_playlists()
        self.add_child(userplaylists)
        
    def _get_xbmc_items(self, list, lvl, flag):
        import qobuz
        childs = self.get_childs()
        for child in self.get_childs():
            item = xbmcgui.ListItem(
                                    child.get_label(), 
                                    child.get_label2(), 
                                    child.get_icon(), 
                                    child.get_thumbnail(), 
                                    child.get_url()
                                    )
            item.setProperty('IsFolder', 'true' if child.is_folder() else 'false')
            item.setIconImage(child.get_icon())
            item.setThumbnailImage(child.get_thumbnail())
            list.append(( child.get_url(), item, child.is_folder() ))
        return True

