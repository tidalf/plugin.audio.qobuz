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
from icacheable import ICacheable
from mydebug import log, info, warn
from utils import _sc
from easytag import QobuzTagTrack
import pprint
'''
 Class QobuzTrack 

 @summary: Manage one qobuz track
 @param qob: parent
 @param id: track id
 @return: New QobuzTrack 
'''
class QobuzTrack(ICacheable):
    # Constructor
    def __init__(self, Core, id, context_type='playlist'):
        self.Core = Core
        self.id = id
        super(QobuzTrack, self).__init__(self.Core.Bootstrap.cacheDir,
                                         'track',
                                         self.id)
        self.set_cache_refresh(self.Core.Bootstrap.__addon__.getSetting('cache_duration_track'))
        info(self, "Cache duration: " + str(self.cache_refresh))
        self.fetch_data()

    # Methode called by parent class ICacheable when fresh data is needed
    def _fetch_data(self):
        return self.Core.Api.get_track(self.id)
        
    # Return track duration
    def get_duration(self):
        (sh,sm,ss) = self._raw_data['duration'].split(':')
        return (int(sh) * 3600 + int(sm) * 60 + int(ss))

