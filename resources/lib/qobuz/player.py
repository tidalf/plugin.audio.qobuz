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

class QobuzPlayer_playlist(xbmc.PlayList):
    def __init__(self, type = xbmc.PLAYLIST_MUSIC):
        super(QobuzPlayer_playlist, self).__init__(type)
        #self.clear()
        
    def getCurrentPos(self, item):
        cpath = item.getProperty('path')
        cstream = item.getProperty('stream') 
        size  =  self.size()
        print "Current path: " + cpath
        cpos = -1
        for i in range(0, size):
            print "Playlist path [" + str(i) + '] ' + self[i].getfilename()
            if cpath == self[i].getfilename():
                cpos += 1
                break
            elif cstream == self[i].getfilename():
                cpos += 1
                break
            else:
                cpos += 1
        print "Current position: " + str(cpos)
        return cpos + 1
    
    def getNextPos(self, cpos):
        if self.size() == 0:
            return None
        if self.size() == cpos:
            return 0
        return (cpos + 1)
    
    def getNextItem(self, item):
        cpos = self.getCurrentPos(item)
        npos = self.getNextPos(cpos)
        return self[npos]
        
    def replacePath(self, cpos, item):
        if cpos > self.size():
            warn("Cannot replace item: out of bound")
            return
        cpath = self[cpos].getfilename()
        if 'http' in cpath:
            print "We already have correct url in playlist... abort"
            return
        item.setPath(item.getProperty('stream'))
        item.setProperty('path', item.getProperty('stream'))
        print "Paht replace: " + item.getProperty('path')
        self.add(url=item.getProperty('stream'), listitem=item, index=cpos)
        #self.remove(cpath)
        
    def to_s(self):
        str = ''
        size = self.size()
        for i in range(0, size):
            str += self[i].getfilename() + ' / ' + self[i].getdescription() + "\n"
        return str

class QobuzPlayer(xbmc.Player):
    def __init__(self, type = xbmc.PLAYER_CORE_AUTO):
        #xbmc.Player.__init__(self, type)
        super(QobuzPlayer, self).__init__(type)
        #self.Player = xbmc.Player
        self.Playlist = QobuzPlayer_playlist( xbmc.PLAYLIST_MUSIC)
        #self.Playlist.clear()
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
        #self.Core.Api.report_streaming_start(self.id)
    
    def onPlayBackNext(self):
        print "Next track pushed"
        
    def onPlayBackEnded(self):
        print "End of playback reached"
        
    def onPlayBackResumed(self):
        print "User pause playback"
        
    def parsePluginPath(self, path):
        pass
        
    def onPlayBackStopped(self):
        pass
#        print "User push stop..."
#        size = self.Playlist.size()
#        print "Playlist size: " + str(size)
#        #cpos = self.Playlist.getposition()
#        pitemnext = self.Playlist.getNextItem(self.item)
#        print "Next item to play: " + pitemnext.getfilename()
        
        
    

    
    def play(self, item):
        print "Playlist:\n"
        print self.Playlist.to_s()
        self.item = item
        if not item.getProperty('stream'):
            warn(self, "Non playable item: " + item.getLabel())
            self.Core.Bootstrap.GUI.showNotificationH('Unplayable track', '')
            return False
        cpos = self.Playlist.getCurrentPos(item)
        if cpos == -1:
            print "Could not find song in playlist"
            return False
        print "Need to play track: " + str(cpos)
        self.Playlist.replacePath(cpos, item)
        #item.setPath(item.getProperty('stream'))
        item.setProperty('path_origin', item.getProperty('path'))
#        if self.isPlayingAudio() == True:
#            print "Player is currently playing a song"
#            super(QobuzPlayer, self).stop()
#            while self.isPlayingAudio() == True:
#                print "Sleeping wainting for song to play"
#                xbmc.sleep(250)
        super(QobuzPlayer, self).playselected(cpos)#item.getProperty('stream'), item)
        item.setPath(item.getProperty('path_origin'))
        #super(QobuzPlayer, self).resume()
        item.select(True)
        xbmcplugin.setResolvedUrl(handle=self.Core.Bootstrap.__handle__,succeeded=True,listitem=item)
        #self.Player.play(self, item.getProperty('stream'), item)
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
        item.setPath(item.getProperty('path_origin'))
        
        #if self.isPlayingAudio():
            
        #self.watchPlayback()
        #self.sendQobuzPlaybackEnded()
        #self.run()
        return True
    
    def set_track_id(self, id):
        if self.id:
            self.last_id = self.id
        self.id = id
    
            
    def watchPlayback( self ):
        while self.isPlayingAudio():
            info(self, "Watching playback: " + str(self.getTime()))
            xbmc.sleep(1000)
        #xbmc.sleep(5000)
        info (self,"End of Playback detected")
