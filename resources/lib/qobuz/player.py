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
from time import time
import re
import math
import pprint

import xbmc
import xbmcplugin
import xbmcgui

from debug import info, warn, log
from data.track import QobuzTrack
from utils.tag import QobuzTagTrack
from data.track_streamurl import QobuzTrackURL


class QobuzPlayable():
    def __init__(self, Core, id):
        self.Core = Core
        self.id = id
        
    def get_stream(self):
        self.pref_format = self.Core.Bootstrap.__addon__.getSetting('streamtype')
        self.pref_format_id = 6
        if self.pref_format == 'mp3':
            self.pref_format_id = 5
        self.tag = QobuzTrackURL(self.Core, self.id, self.pref_format_id)
        self.data_url = self.tag.get_data()
        if not self.data_url:
            warn(self, "Cannot resolve url for track id: " + str(id))
            return False
        if int(self.data_url['format_id']) == 6:
            self.format_name = 'flac'
            self.mimetype = 'audio/flac'
        else:
            self.format_name = 'mp3'
            self.mimetype = 'audio/mpeg'
        return True
    
    def getXbmcItem(self):    
        track = QobuzTrack(self.Core, self.id)
        if not track:
            warn(self, "Cannot get QobuzTrack with id: " + str(self.id))
            return None
        tag = QobuzTagTrack(self.Core, track.get_data())
        item = tag.getXbmcItem('player')
        item.setProperty('streaming_url', self.data_url['streaming_url'])
        item.setPath(self.data_url['streaming_url'])
        item.setProperty('mimetype', self.mimetype)
        item.setProperty('IsPlayable', 'true')
        item.setProperty('Music', 'true')
        return item
    
class QobuzPlayer(xbmc.Player):
    def __init__(self, type = xbmc.PLAYER_CORE_DVDPLAYER):
        super(QobuzPlayer, self).__init__()
        
    def setCore (self, Core):
        self.Core = Core
        
    def sendQobuzPlaybackEnded(self, duration):
        self.Core.Api.report_streaming_stop(self.id, duration)
    
    def sendQobuzPlaybackStarted(self,):
        self.Core.Api.report_streaming_start(self.id)
        
    def play(self, id, pos):
        print "Need to play song with id: " + str(id)
        playable = QobuzPlayable(self.Core, id)
        if not playable.get_stream():
            warn(self, "Cannot get stream url for track with id: " + str(id))
            self.Core.Bootstrap.GUI.showNotificationH('Qobuz Player', 'Fail to play song...')
            return False
        item = playable.getXbmcItem()
        '''
            PLaying track
        '''
        self.Core.Bootstrap.GUI.showNotificationH('Playing song', item.getLabel())
        xbmcplugin.setResolvedUrl(handle=self.Core.Bootstrap.__handle__,succeeded=True,listitem=item)
        xbmc.executebuiltin('Dialog.Close(all,true)')
        '''
            Waiting for song to start
        '''
        timeout = 30
        info(self, "Waiting song to start")
        while timeout > 0:
            if self.isPlayingAudio() == False:
                xbmc.sleep(250)
                timeout-=0.250
            else: 
                break
        if timeout <= 0:
            warn(self, "Player can't play track: " + self.item.getLabel())
            super(QobuzPlayer, self).play(item.getProperty('path'))
            return False
        return True
        '''
            Watching playback
#        '''
        return True


#        self.watchPlayback()
#        warn(self, 'stopping player for track: ' + self.item.getLabel())
#        return True
    
            
#    def watchPlayback( self):
#        nextisresolved = False
#        isNotified = False
#        playedTime = 0
#        previousTime = 0
#        self.watching = True
#        pos = self.cpos
#        while self.isPlayingAudio(): 
#            try:
#                if playedTime:
#                    previousTime = playedTime
#                playedTime = self.getTime()
#            except:
#                warn(self, "Cannot getTime(), player may be not running") 
#            timeleft = None
#            if playedTime:
#                if previousTime:
#                    if playedTime < previousTime:
#                        print "Track Changed"
#                        playedTime = 0
#                        previousTime = 0
#                        nextisresolved = False
#                        isNotified = False
#                        pos = self.Playlist.get_next_pos(pos)
#                try:
#                    timeleft = self.getTotalTime() - playedTime
#                except:
#                    warn(self, "Cannot getTotalTime(), player may be not running")
#            if (timeleft != None) and (timeleft < 20):
#                if not nextisresolved:
#                    ''' 
#                    Prefetch next streaming url
#                    '''
#                    npos = self.Playlist.get_next_pos(pos)
#                    item = None #self.Playlist.resolve_url_at_pos(npos)
#                    if item:
#                        self.Core.Bootstrap.GUI.showNotificationH('Qobuz Player', 'Next Song: ' + item.getLabel())
#                        nextisresolved = True
#                    #nextisresolved = self.prefetch_next_url(self.Playlist.getposition())
#                    pass
#            if not isNotified and playedTime > 6:
#                self.sendQobuzPlaybackStarted()
#                isNotified = True
#            if math.trunc(math.floor(playedTime)) % 5 == 0:
#                info(self, 'Played time: ' + str(playedTime))
#                #info(self, "Playlist:\n" + self.Playlist.to_s())
#            xbmc.sleep(250)
#        if playedTime > 6:
#            self.sendQobuzPlaybackEnded(playedTime)
#        info(self, "Stop watching playback (" + self.item.getLabel() + ' / ' + str(playedTime) + 's')
    
