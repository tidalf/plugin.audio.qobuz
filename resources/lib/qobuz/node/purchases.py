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
from debug import info, warn, error, debug
#from tag.track import TagTrack
#from tag.product import TagProduct
'''
    NODE PURCHASES
'''
from cache.purchases import Cache_purchases
from cache.product import Cache_product
#from tag.product import TagProduct
#from tag.album import TagAlbum
from product import Node_product

class Node_purchases(Node):

    def __init__(self, parent = None, params = None):
        super(Node_purchases, self).__init__(parent)
        self.label = qobuz.lang(30100)
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_PURCHASES
        self.set_content_type('albums')
        self.cache = Cache_purchases()
        self.icon = self.thumb = qobuz.image.access.get('album')
    
    def _build_down(self, lvl, flag = None):
        data = self.fetch_data()
        print "DATA: " + pprint.pformat(data)
        if not data: 
            error(self, "Cannot fetch purchases data")
            return False
        self.set_data(data)
        for product in self.cache.filter_products(self.cache.get_data()):
            self.add_child(product)

    def _get_xbmc_items(self, list, lvl, flag):
        if len(self.childs) < 1:
            qobuz.gui.notify(36000, 36001)
            return False
        for product in self.childs:
            if product.filter(flag): continue
            item = product.make_XbmcListItem()#tag.getXbmcItem()
            self.attach_context_menu(item, product)
            list.append((product.get_url(Mode.VIEW), item, product.is_folder()))
        return True
