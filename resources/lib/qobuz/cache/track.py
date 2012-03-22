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

from icacheable import ICacheable
from debug import *

import pprint
import qobuz

'''
 Class QobuzTrack 

 @summary: Manage one qobuz track
 @param qob: parent
 @param id: track id
 @return: New QobuzTrack 
'''
class Cache_track(ICacheable):

    def __init__(self, id, context_type = 'playlist', auto_fetch = True):
        self.id = id
        super(Cache_track, self).__init__(qobuz.path.cache,
                                         'track',
                                         self.id, True)
        self.set_cache_refresh(qobuz.addon.getSetting('cache_duration_track'))
        debug(self, "Cache duration: " + str(self.cache_refresh))

    def _fetch_data(self):
        json = qobuz.api.get_track(self.id)
        print pprint.pformat(json)
        return json

