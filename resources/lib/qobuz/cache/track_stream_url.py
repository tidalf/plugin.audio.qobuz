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
from debug import info, warn, error, debug
import pprint
import qobuz
'''
 Class QobuzTrackURL

 @summary: Manage one qobuz track streaming url
 @param qob: parent
 @param id: track id
 @return: New QobuzTrackURL
'''
class Cache_track_stream_url(ICacheable):
    # Constructor
    def __init__(self, id):
        self.id = id
        self.format_id = 6
        if qobuz.addon.getSetting('streamtype') == 'mp3':
            self.format_id = 5
        super(Cache_track_stream_url, self).__init__(qobuz.path.cache,
                                            'track-url-' + str(self.format_id),
                                            self.id, False)
        self.set_cache_refresh(qobuz.addon.getSetting('cache_duration_auth'))
        info(self, "Cache duration: " + str(self.cache_refresh))
        self.fetch_data()

    # Methode called by parent class ICacheable when fresh data is needed
    def _fetch_data(self):
        data = qobuz.api.get_track_url(self.id, 'playlist', 0, self.format_id)
        return data
