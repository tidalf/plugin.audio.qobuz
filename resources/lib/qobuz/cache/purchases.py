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
#from tag.track import TagTrack
#from tag.album import TagAlbum
from node.product import Node_product
import qobuz
"""
    Class QobuzGetPurchases
"""
class Cache_purchases(ICacheable):

    def __init__(self, limit = 100):
        self.limit = limit
        super(Cache_purchases, self).__init__(qobuz.path.cache, 
                                       'purchases')
        self.set_cache_refresh(qobuz.addon.getSetting('cache_duration_recommandation'))
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
#            ''' 
#            Little hack, we are injecting missing informations into
#            json that we have to pass to Node_product
#
#            '''
            json[u'composer'] = track['composer']
            json[u'interpreter'] = track['interpreter']
#            print "Composer: " + json['composer']['name']
            product = Node_product()
            product.set_data(json)
            id = product.get_id()
            print "Artist: " + product.get_artist()
            print "ProductID: " + id
            print "Track: " + pprint.pformat(json)
            if id in blackid: continue
            if id in albumseen: continue
            #if albumseen[id]: continue
            print "LABEL " + product.get_label()
            albumseen[id] = 1
            list.append(product)
        return list
            
    def get_items(self):
        list = []
        data = self.get_data()
        if not data: return list
        n = self.length()
        for a in self.filter_products(self._raw_data):
            item = a[0].getXbmcItem('fanArt')
            item.setInfo('music', infoLabels = { 'artist': a[0].getArtist(), 'year': a[1].getYear()})
            u = qobuz.boot.build_url(MODE_ALBUM, a[0].id)
            list.append((u, item, True))        
        return list

