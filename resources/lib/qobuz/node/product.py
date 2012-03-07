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
from node import Node
from debug import info
'''
    NODE PRODUCT
'''
from cache.product import Cache_product

from track import Node_track

class Node_product(Node):

    def __init__(self, parent = None, params = None):
        super(Node_product, self).__init__(parent)
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_PRODUCT
        self.set_content_type('songs')


    def _build_down(self, lvl, flag = None):
        pass

    def _get_xbmc_items(self, list, lvl, flag):
        pass

    def _get_tag_items(self, list, lvl, flag):
        pass



