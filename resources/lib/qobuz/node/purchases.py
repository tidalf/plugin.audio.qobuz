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
import qobuz
from flag import NodeFlag
from node import Node
from product import Node_product

from debug import error

'''
    NODE PURCHASES
'''

from cache.purchases import Cache_purchases
#from product import Node_product

class Node_purchases(Node):

    def __init__(self, parent = None, params = None):
        super(Node_purchases, self).__init__(parent, params)
        self.label = qobuz.lang(30100)
        self.type = NodeFlag.TYPE_NODE | NodeFlag.TYPE_PURCHASES
        self.set_content_type('albums')
        self.cache = Cache_purchases()
        self.image = qobuz.image.access.get('album')
    
    def _build_down(self, xbmc_directory,  lvl, flag = None, progress = None):
        data = self.fetch_data()
        if not data: 
            error(self, "Cannot fetch purchases data")
            return False
        self.set_data(data)
        for product in self.filter_products(self.cache.get_data()):
            self.add_child(product)
        return True
    
    def filter_products(self, data):
        list = []
        if not data: return list
        # Qobuz free tracks with invalid product id
        #blackid = ['0000020110926', '0000201011300', '0000020120220', '0000020120221']
        albumseen = {}
        for track in data['albums']['items']:
            json = track
            # json[u'composer'] = track['composer']
            json[u'interpreter'] = track['artist']['name']
            product = Node_product()
            product.set_data(json)
            id = product.get_id()
            #if id in blackid: product.is_special_purchase = True
            if id in albumseen: continue
            albumseen[id] = 1
            list.append(product)
        return list
 
