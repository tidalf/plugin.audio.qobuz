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
import xbmcgui
from mydebug import info, warn, log
from time import time
from track import QobuzTrack
import re
import threading
import math

class QobuzPlayer_playlist(xbmc.PlayList):
    def __init__(self, type = xbmc.PLAYLIST_MUSIC):
        super(QobuzPlayer_playlist, self).__init__(type)
        
    def getCurrentPos(self, item):
        cpath = item.getProperty('path')
        cstream = item.getProperty('stream')
        print "CPATH: " + cpath
        print "CSTREAM: " + cstream 
        size  =  self.size()
        cpos = -1
        for i in range(0, size):
            filename =  self[i].getfilename()   
            print "MATCH: " + filename   
            if cpath == filename:
                cpos = i
                break
            elif cstream == filename:
                cpos = i
                break
        print "Current position: " + str(cpos)
        return cpos
    
    def is_valid_position(self, cpos):
        if cpos < 0:
            warn(self, "Playlist index < 0")
            return False
        if cpos >= self.size():
            warn(self, "Playlist index > 0")
            return False
        return True
    
    def prefetching_needed(self, pos):
        if not self.is_valid_position(pos):
            warn(self, "Playlist positon is not valid: " + pos)
            return False
        if 'http://' in self[pos].getfilename():
            info(self, 'URL is already resolved')
            return False
        return True
        
    def getNextPos(self, cpos):
        if self.size() == 0:
            return None
        if (cpos + 1) >= self.size():
            return 0
        return (cpos + 1)
    
    def getNextItem(self, item):
        cpos = self.getCurrentPos(item)
        npos = self.getNextPos(cpos)
        if not npos:
            return None
        return self[npos]
        
    def replacePath(self, cpos, item):
        if not self.is_valid_position(cpos):
            warn(self, "Cannot replace url (index out of bound)")
            return False
        cpath = self[cpos].getfilename()
        if not cpath:
            warn(self, 'Current path is empty, abort')
            return False
        if 'http' in cpath:
            print "We already have correct url in playlist... abort"
            return True
        print "Path replace: " + item.getProperty('path')
        newitem = xbmcgui.ListItem(item.getProperty('path'), '', '', path=item.getProperty('stream'))
        self.remove(cpath)
        self.add(url=item.getProperty('stream'), listitem=item, index=cpos)
        return True
    
    def to_s(self):
        size = self.size()
        s = 'Size: ' + str(size) + "\n"
        for i in range(0, size):
            s += '[' + str(i) + '] ' + self[i].getfilename() + ' / ' + self[i].getdescription() + "\n"
        return s

class QobuzPlayer(xbmc.Player):
    def __init__(self, type = xbmc.PLAYER_CORE_AUTO):
        super(QobuzPlayer, self).__init__(type)
        self.Playlist = QobuzPlayer_playlist( xbmc.PLAYLIST_MUSIC)
        self.id = None
        self.last_id = None
        self.Core = None
        self.startPlayingOn = None
        self.item = None
        self.playedTime = None
    
    def setApi (self, Core):
        self.Core = Core
        
    def sendQobuzPlaybackEnded(self, duration):
        self.Core.Api.report_streaming_stop(self.id, duration)
    
    def sendQobuzPlaybackStarted(self,):
        self.Core.Api.report_streaming_start(self.id)
    
#    def onPlayBackStarted(self):
#        print "Playback started"
#    
##    def onPlayBackNext(self):
##        print "Next track pushed"
#        
#    def onPlayBackEnded(self):
#        print "End of playback reached"
        
#    def onPlayBackResumed(self):
#        print "User pause playback"
        
    def parsePluginPath(self, path):
        print "searchin in path: " + path
        m = re.search('id=(\d+)', path)
        if not m:
            warn(self, "No id in playlist path")
            return None
        print "Next track id: " + m.group(1)
        return m
        
    def onPlayBackStopped(self):
        pass
    
    def prefetch_url(self, id):
        return self.Core.getTrackURL(id, 5)
        
    def prefetchNextURL(self, cpos):
        npos = self.Playlist.getNextPos(cpos)
        print "Npos: " + str(npos)
        if npos == None or npos == -1:
            warn(self, "Cannot get next position")
            return False
        if 'http' in self.Playlist[npos].getfilename():
            print "Next url is good... skip"
            return True
        parsed = self.parsePluginPath(self.Playlist[npos].getfilename())
        if not parsed:
            warn(self, "Cannot get next track id")
            return False
        t = QobuzTrack(self.Core, int(parsed.group(1)))
        item = t.getItem()
        if not item.getProperty('stream'):
            warn(self, "Next item is not playable... removing")
            self.Playlist.remove(item.getProperty('path'))
            return False
        self.Playlist.replacePath(npos, item)
        return True
    
    def play(self, id, pos):
        pos = int(pos)
        track = self.Core.getTrack(id)
        self.item = track.getItem()
        self.cpos = pos #int(self.Core.Bootstrap.params['pos'])
        url = None
        if self.Playlist.prefetching_needed(pos):
            tu = self.prefetch_url(id)
            if not tu:
                warn(self, 'Cannot fetch streaming url')
                return False
            url = tu.get_data()['streaming_url']
        else:
            url = self.Playlist[pos].getfilename()
        if not url:
            warn("We don't have url to play track")
            return False
        self.item.setPath(url)
        self.item.setProperty('mimetype', 'audio/flac')
        self.item.setProperty('stream', url)
        if not self.item.getProperty('stream'):
            warn(self, "Non playable item: " + item.getLabel())
            self.Core.Bootstrap.GUI.showNotificationH('Qobuz Player', 'Track is not playable')
            return False
        self.Core.Bootstrap.GUI.showNotificationH('Qobuz Player', 'Starting song')
        self.Playlist.replacePath(self.cpos, self.item)
        super(QobuzPlayer, self).playselected(self.cpos)
        xbmcplugin.setResolvedUrl(handle=self.Core.Bootstrap.__handle__,succeeded=True,listitem=self.item)
        xbmc.executebuiltin('Dialog.Close(all, true)')
        timeout = 30
        info(self, "Waiting song to start")
        while timeout > 0:
            if self.isPlayingAudio() == False:
                xbmc.sleep(1000)
                timeout-=1
            else: 
                break
        if timeout <= 0:
            warn(self, "Player can't play track: " + self.item.getLabel())
            return False
        self.set_track_id(self.Core.Bootstrap.ID)
        #self.prefetchNextURL(cpos + 1)
        self.watchPlayback()
        warn(self, 'stopping player for track: ' + self.item.getLabel())
    
    def set_track_id(self, id):
        if self.id:
            self.last_id = self.id
        self.id = id
    
            
    def watchPlayback( self):
        nextisreplaced = False
        isNotified = False
        playedTime = None
        while self.isPlayingAudio():
            try:
                playedTime = self.getTime()
            except:
                warn(self, "Cannot getTime(), player may be not running") 
            timeleft = None
            if playedTime:
                try:
                    timeleft = self.getTotalTime() - playedTime
                except:
                    warn(self, "Cannot getTotalTime(), player may be not running")
            if (timeleft != None) and (timeleft < 20):
                if not nextisreplaced:
                    nextisreplaced = self.prefetchNextURL(self.Playlist.getposition())
            if not isNotified and playedTime > 6:
                self.sendQobuzPlaybackStarted()
                isNotified = True
            if math.trunc(math.floor(playedTime)) % 5 == 0:
                info(self, 'Played time: ' + str(playedTime))
                info(self, "Playlist:\n" + self.Playlist.to_s())
            xbmc.sleep(1000)
        if playedTime > 6:
            self.sendQobuzPlaybackEnded(playedTime)
        info(self, "Stop watching playback (" + self.item.getLabel() + ' / ' + str(playedTime) + 's')
    
