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
from tree.node import Node
from debug import info
from tag.track import TagTrack
from tag.product import TagProduct
'''
    NODE PURCHASES
'''
from data.purchases import QobuzGetPurchases
from data.product import QobuzProduct
from tag.product import TagProduct
from tag.album import TagAlbum
from node_product import node_product

class node_purchases(Node):
    
    def __init__(self, parent = None, params = None):
        super(node_purchases, self).__init__(parent)
        self.label  = 'Product'
        self.label2 = 'Keep your current playlist'
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_PURCHASES
        self.set_content_type('albums')
        
    def _build_down(self, lvl, flag = None):
        o = QobuzGetPurchases()
        data = o.get_data()
        print "DATA: " + repr(data)
        if not data: return
        self.set_json(data)
        for a in o.filter_products(o._raw_data):
            p = node_product(a[0].id)
            p.set_id(a[0].id)
            product_json = a[1].get_json()['album']
            p.set_json(product_json)
            p.set_url()
            self.add_child(p)

    def _get_xbmc_items(self, list, lvl, flag):
        if len(self.childs) < 1:
            return False
        for c in self.childs:
            pre_tag = TagProduct(c.get_json())
            cache = QobuzProduct(pre_tag.id)
            tag = TagProduct(cache.get_data()) 
            item = tag.getXbmcItem()
            url = c.get_url()
            print "URL: " + url
            item.setPath(url)
            print "Path: " + item.getProperty('Path')
            item.setProperty('path', url)
            #item.setLabel(''.join((tag.getArtist(), ' - ', tag.getAlbum())))
            list.append((item.getProperty('path'), item, True))
        return True