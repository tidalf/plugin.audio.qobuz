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
import qobuz

class QobuzPlayable():
    def __init__(self, id):
        self.id = id
        
    def get_stream(self):
        self.pref_format = qobuz.addon.getSetting('streamtype')
        self.pref_format_id = 6
        if self.pref_format == 'mp3':
            self.pref_format_id = 5
        self.tag = QobuzTrackURL(self.id, self.pref_format_id)
        self.data_url = self.tag.get_data()
        #print "Dataurl: " + str(self.data_url)
        if not self.data_url:
            warn(self, "Cannot resolve url for track id: " + str(id))
            return False
        #print "Plop"
        #pprint.pprint(self.data_url)
        if int(self.data_url['format_id']) == 6:
            self.format_name = 'flac'
            self.mimetype = 'audio/flac'
        else:
            self.format_name = 'mp3'
            self.mimetype = 'audio/mpeg'
        return True
    
    def getXbmcItem(self):  
        track = QobuzTrack(self.id)
        try:
            db = qobuz.db
            db_track = db.insert_track(track.get_data())
            if db_track:
                pc = db_track['played_count']
                if not pc: pc = 1
                else: pc += 1
                db.update_track(db_track['track_id'], 'played_count', pc)
                db.update_track(db_track['track_id'], 'last_played_on', int(time()))
                if not track:
                    warn(self, "Cannot get QobuzTrack with id: " + str(self.id))
                    #return None
        except: warn(self, 'SQLite Error while tracking track :)')
        tag = QobuzTagTrack(track.get_data())
        item = tag.getXbmcItem('player')
        item.setProperty('streaming_url', self.data_url['streaming_url'])
        item.setPath(self.data_url['streaming_url'])
        item.setProperty('mimetype', self.mimetype)
        item.setProperty('IsPlayable', 'true')
        item.setProperty('Music', 'true')
        return item
    
class QobuzPlayer(xbmc.Player):
    def __init__(self, type = xbmc.PLAYER_CORE_AUTO):
        super(QobuzPlayer, self).__init__()
        
    def sendQobuzPlaybackEnded(self, duration):
        qobuz.api.report_streaming_stop(self.id, duration)
    
    def sendQobuzPlaybackStarted(self,):
        qobuz.api.report_streaming_start(self.id)
        
    def play(self, id):
        lang = qobuz.lang
        info(self, "We need to play song with id: " + str(id))
        playable = QobuzPlayable(id)
        if not playable.get_stream():
            warn(self, "Cannot get stream url for track with id: " + str(id))
            qobuz.gui.showNotification(34000, 34002)
            return False
        item = playable.getXbmcItem()
        '''
            PLaying track
        '''
        qobuz.gui.showNotificationH(lang(34000), item.getLabel())
        #super(QobuzPlayer, self).play(item.getProperty('streaming_url'))
        xbmcplugin.setResolvedUrl(handle=qobuz.boot.handle,succeeded=True,listitem=item)
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
            warn(self, "Player can't play track: " + item.getLabel())
            
            return False
        return True
