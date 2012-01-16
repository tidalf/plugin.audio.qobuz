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
import os
import sys
import pprint

import xbmcaddon
import xbmcplugin
import xbmcgui
import xbmc


from utils.icacheable import ICacheable
from debug import *
#from utils import _sc
from constants import *
from utils.tag import QobuzTagProduct
from utils.tag import QobuzTagTrack
import qobuz

###############################################################################
# Class QobuzProduct
###############################################################################
class QobuzProduct(ICacheable):

    def __init__(self, id, context_type = "playlist" ):
        self.id = id
        self.context_type = context_type
        super(QobuzProduct, self).__init__( qobuz.path.cache, 
                                          'product',
                                          self.id)
        self.set_cache_refresh(qobuz.addon.getSetting('cache_duration_album'))
        info(self, "Cache duration: " + str(self.cache_refresh))
        self.fetch_data()

    def _fetch_data(self):
        data = qobuz.api.get_product(str(self.id), self.context_type)['product']
        return data

    def length(self):
        return len(self._raw_data['tracks'])

    def get_items(self):
        tag_product = QobuzTagProduct(self.get_data())
        list = []
        for tag_track in tag_product.get_childs():
            if not isinstance(tag_track, QobuzTagTrack):
                continue
            item = tag_track.getXbmcItem('album')
            u = qobuz.boot.build_url(MODE_SONG, tag_track.id)
            list.append((u, item, False))
        return list
