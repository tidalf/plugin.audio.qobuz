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

class QobuzPlayer_playlist(xbmc.PlayList):
    def __init__(self, type = xbmc.PLAYLIST_MUSIC):
        super(QobuzPlayer_playlist, self).__init__(type)
        #self.clear()
        
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
        if cpos > self.size():
            warn(self, "Cannot replace item: out of bound")
            return False
        
        cpath = self[cpos].getfilename()
        if not cpath:
            warn(self, 'Current path is empty, abort')
            return False
        if 'http' in cpath:
            print "We already have correct url in playlist... abort"
            return
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
    
    def setApi (self, Core):
        self.Core = Core
    
    def playnext(self):
        info(self, "Playing next track...")
        
    def sendQobuzPlaybackEnded(self):
        duration = None
        try:
            duration = time() - self.startPlayingOn
        except: 
            warn(self, "Cannot calcul duration, don't send api/stop")
            return
        self.Core.Api.report_streaming_stop(self.id, duration)
    
    def onPlayBackStarted(self):
        print "Playback started"
    
    def onPlayBackNext(self):
        print "Next track pushed"
        
    def onPlayBackEnded(self):
        print "End of playback reached"
        
    def onPlayBackResumed(self):
        print "User pause playback"
        
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
        
    def prefetchNextURL(self, cpos):
        npos = self.Playlist.getNextPos(cpos)
        print "Npos: " + str(npos)
        if not npos:
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
    
    def play(self, item):
        self.item = item
        if not item.getProperty('stream'):
            warn(self, "Non playable item: " + item.getLabel())
            self.Core.Bootstrap.GUI.showNotificationH('Qobuz Player', 'Track is not playable')
            return False
        self.Core.Bootstrap.GUI.showNotificationH('Qobuz Player', 'Starting song')
        self.cpos = int(self.Core.Bootstrap.params['pos'])
        self.Playlist.replacePath(self.cpos, item)
        self.prefetchNextURL(self.cpos)
        super(QobuzPlayer, self).playselected(self.cpos)
        item.setPath(item.getProperty('path'))
        xbmcplugin.setResolvedUrl(handle=self.Core.Bootstrap.__handle__,succeeded=True,listitem=item)
        timeout = 30
        info(self, "Waiting song to start")
        while timeout > 0:
            if self.isPlayingAudio() == False:
                xbmc.sleep(1000)
                timeout-=1
            else: 
                break
        if timeout <= 0:
            warn(self, "Player can't play track: " + item.getLabel())
            return False
        #xbmcplugin.setResolvedUrl(handle=self.Core.Bootstrap.__handle__,succeeded=True,listitem=item)
        self.startPlayingOn = time()
        #xbmc.executebuiltin('Container.Refresh()')
        self.set_track_id(self.Core.Bootstrap.ID)
        self.Core.Api.report_streaming_start(self.id)
        self.Core.Bootstrap.GUI.showNotificationH('Qobuz Player', 'Playing song')
        self.watchPlayback()
        exit(0)
    
    def set_track_id(self, id):
        if self.id:
            self.last_id = self.id
        self.id = id
    
            
    def watchPlayback( self ):
        nextisreplaced = False
        while self.isPlayingAudio():
            info(self, "Watching playback: " + str(self.getTime()))
            try:
                timeleft = self.getTotalTime() - self.getTime()
                if timeleft < 20:
                    #if nextisreplaced == False:
                    nextisreplaced = self.prefetchNextURL(self.Playlist.getposition() + 1)
            except:
                warn(self, 'Prefetching next url fail!')
            xbmc.sleep(1000)
        self.sendQobuzPlaybackEnded()
        #self.Core.Bootstrap.GUI.showNotificationH('Qobuz Player', 'End of song')
        info (self,"End of Playback detected")
