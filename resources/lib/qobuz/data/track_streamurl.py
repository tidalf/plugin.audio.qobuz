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

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

from utils.icacheable import ICacheable
from debug import log, info, warn
#from utils import _sc
import pprint
import qobuz
'''
 Class QobuzTrackURL

 @summary: Manage one qobuz track streaming url
 @param qob: parent
 @param id: track id
 @return: New QobuzTrackURL
'''
class QobuzTrackURL(ICacheable):
    # Constructor
    def __init__(self, id, type):
        self.id = id
        self.type = type
        self.format_id = 6
        if qobuz.addon.getSetting('streamtype') == 'mp3':
            self.format_id = 5
        super(QobuzTrackURL, self).__init__(qobuz.path.cache,
                                            'track-url-' + str(self.format_id),
                                            self.id)
        self.set_cache_refresh(qobuz.addon.getSetting('cache_duration_auth'))
        info(self, "Cache duration: " + str(self.cache_refresh))
        self.fetch_data()

    # Methode called by parent class ICacheable when fresh data is needed
    def _fetch_data(self):
        return qobuz.api.get_track_url(self.id, 'playlist', 0,  self.format_id)
