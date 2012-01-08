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
        #xp.add( item.getProperty('stream'), item)
#        item.setProperty('oldpath', item.getProperty('path'))
#        item.setProperty('path', item.getProperty('stream'))
        #player.play(item.getProperty('stream'), item, False)
#        item.setProperty('path', item.getProperty('oldpath'))
        #xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]),succeeded=True,listitem=item)
        #player.play(item.getProperty('stream'), item, False)
        print 'Path: ' + item.getProperty('path')
        item.setProperty('path_origin', item.getProperty('path'))
        item.setPath(item.getProperty('stream'))
        xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]),succeeded=True,listitem=item)
        #item.setProperty('path', item.getProperty('stream'))
        #xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]),succeeded=True,listitem=item)
        timeout = 30
        info(self, "Waiting song to start")
        while timeout > 0:
            if player.isPlayingAudio == False:
                time.sleep(.500)
                timeout-=.500
            else: timeout = 0
        info(self, "Song started: " + item.getProperty('image'))
        item.setPath(item.getProperty('path_origin'))
        #item.setProperty('path', item.getProperty('stream'))
#        item.setPath(item.getProperty('path'))
#        item.setThumbnailImage(item.getProperty('image'))
#        item.setIconImage(item.getProperty('image'))
        #item.select(True)
        xbmc.sleep(6000)
        if player.isPlayingAudio():
            self.Core.Api.report_streaming_start(self.id)
        player.watchPlayback()
        #player.onPlayBackEnded('stop_track('+str(self.id)+')')

