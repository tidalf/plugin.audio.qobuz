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
import os
import xbmcgui
import xbmcplugin

import pprint

from debug import *
from constants import *
from utils.icacheable import ICacheable
from node.product import Node_product
import qobuz
"""
    Class QobuzGetPurchases
"""
class Cache_purchases(ICacheable):

    def __init__(self, limit = 100):
        self.limit = limit
        super(Cache_purchases, self).__init__(qobuz.path.cache, 
                                       'purchases', None, False)
        self.set_cache_refresh(qobuz.addon.getSetting('cache_duration_recommendation'))
        debug(self, "Cache duration: " + str(self.cache_refresh))
        self.fetch_data()
        
    def _fetch_data(self):
        return qobuz.api.get_purchases(self.limit)
    
    def length(self):
        if not self._raw_data:
            return 0
        return len(self._raw_data)

    def filter_products(self, data):
        list = []
        if not data: return list
        # Qobuz free tracks with invalid product id
        blackid = ['0000020110926', '0000201011300']
        albumseen = {}
        for track in data:
            json = track['album']
            json[u'composer'] = track['composer']
            json[u'interpreter'] = track['interpreter']
            product = Node_product()
            product.set_data(json)
            id = product.get_id()
            if id in blackid: continue
            if id in albumseen: continue
            print "LABEL " + product.get_label()
            albumseen[id] = 1
            list.append(product)
        return list
            
