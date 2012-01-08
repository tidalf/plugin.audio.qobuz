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
import xbmc
import xbmcplugin
from mydebug import info, warn, log
from time import time

class QobuzPlayer(xbmc.Player):
    def __init__(self, type):
        xbmc.Player.__init__(self)
        #super(QobuzPlayer, self).__init__(type)
        self.id = None
        self.last_id = None
        self.Core = None
        self.startPlayingOn = None
        self.item = None
    
    def setApi (self, Core):
        self.Core = Core
    
    def onPlayBackStarted(self):
        info(self, "Playback started")
        self.startPlayingOn = time()
    
    def sendQobuzPlaybackEnded(self):
        duration = None
        try:
            duration = time() - self.startPlayingOn
        except: 
            warn(self, "Cannot calcul duration, don't send api/stop")
            return
        self.Core.Api.report_streaming_stop(self.id, duration)
    
    def onPlayBackEnded(self):
        info(self, 'onPlayBackEnded()')
        xbmc.sleep(10000)
        
    def play(self, item):
        self.item = item
        item.setProperty('path_origin', item.getProperty('path'))
        item.setPath(item.getProperty('stream'))
        xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]),succeeded=True,listitem=item)
        timeout = 30
        info(self, "Waiting song to start")
        while timeout > 0:
            if self.isPlayingAudio == False:
                xbmc.sleep(1000)
                timeout-=1
            else: timeout = 0
        xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]),succeeded=True,listitem=item)
        item.setPath(item.getProperty('path_origin'))
        if self.isPlayingAudio():
            self.Core.Api.report_streaming_start(self.id)
            self.watchPlayback()
        self.sendQobuzPlaybackEnded()
        return 0
    
    def set_track_id(self, id):
        if self.id:
            self.last_id = self.id
        self.id = id

    def watchPlayback( self ):
        while self.isPlayingAudio():
            xbmc.sleep(1000)
        info (self,"End of Playback detected")