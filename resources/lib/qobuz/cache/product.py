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

from icacheable import ICacheable
from debug import *
from constants import *
import qobuz

###############################################################################
# Class QobuzProduct
###############################################################################
class Cache_product(ICacheable):

    def __init__(self, id, context_type = "playlist"):
        self.id = id
        self.context_type = context_type
        super(Cache_product, self).__init__(qobuz.path.cache,
                                          'product',
                                          self.id)
        self.set_cache_refresh(qobuz.addon.getSetting('cache_duration_album'))
        info(self, "Cache duration: " + str(self.cache_refresh))
        self.fetch_data()

    def _fetch_data(self):
        data = qobuz.api.get_product(str(self.id), self.context_type)
        if not data: return None
        return data

    def length(self):
        return len(self._raw_data['tracks'])
