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
from player import QobuzPlayer
from easytag import QobuzTagTrack
'''
 Class QobuzTrack 

 @summary: Manage one qobuz track
 @param qob: parent
 @param id: track id
 @return: New QobuzTrack 
'''
class QobuzTrack(ICacheable):
    # Constructor
    def __init__(self,qob,id):
        self.Core = qob
        self.id = id
        self._raw_data = []
        self.cache_path = os.path.join(self.Core.Bootstrap.cacheDir,
                                        'track-' + str(self.id) + '.dat')
        self.cache_refresh = self.Core.Bootstrap.__addon__.getSetting('cache_duration_track')
        info(self, "Cache duration: " + str(self.cache_refresh))
        self.format_id = 6
        settings = xbmcaddon.Addon(id='plugin.audio.qobuz')
        # Todo : Due to caching, streaming url can be mixed if settings are 
        # changed
        if settings.getSetting('streamtype') == 'mp3':
            self.format_id = 5
        self.fetch_data()

    # Methode called by parent class ICacheable when fresh data is needed
    def _fetch_data(self):
        data = {}
        data['info'] = self.Core.Api.get_track(self.id)
        return data
        
    # Return track duration
    def get_duration(self):
        (sh,sm,ss) = self._raw_data['info']['duration'].split(':')
        return (int(sh) * 3600 + int(sm) * 60 + int(ss))

    # Build an XbmcItem based on json data
    def getItem(self):
        '''
            This hack work but we must stick with the real API and pass
            album_id and context?
        '''
        album_id = ''
        t = QobuzTagTrack(self._raw_data)
        item = t.getXbmcItem()
        stream = self.Core.Api.get_track_url(self.id,
                                                    'playlist',
                                                    album_id,
                                                    self.format_id)
        mimetype = 'audio/flac'
        if self.format_id == 5:
            mimetype = 'audio/mpeg'
        item.setProperty('mimetype', mimetype)
        item.setProperty('stream', str(stream['streaming_url']))
        return item
    
    def stop(self, id):
        self.Core.Api.report_streaming_stop(self.id)
    
    
    
    # Play this track
    def play(self):
        #global player
        player = QobuzPlayer(xbmc.PLAYER_CORE_AUTO)
        player.set_track_id(self.id)
        player.setApi(self.Core)
        item = self.getItem()
        player.play(item)

