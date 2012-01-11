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
from easytag import QobuzTagTrack
import re
import threading
import math
import pprint

class QobuzPlayer_playlist(xbmc.PlayList):
    def __init__(self, type = xbmc.PLAYLIST_MUSIC):
        super(QobuzPlayer_playlist, self).__init__()
        
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
            warn(self, "Playlist positon is not valid: " + str(pos))
            return False
        if 'http://' in self[pos].getfilename():
            info(self, 'URL is already resolved')
            return False
        info(self, "Need to prefetch playlist item at index: " + str(pos))
        return True
        
    def get_next_pos(self, cpos):
        size = self.size()
        if size == 0:
            return -1
        cpos += 1
        if cpos < size:
            return cpos
        return 0
           
#    def getNextItem(self, item):
#        cpos = self.getCurrentPos(item)
#        npos = self.getNextPos(cpos)
#        if not npos:
#            return None
#        return self[npos]
        
    def replace_path(self, cpos, item):
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
        command = 'Container.update("%s","%s")' % ( cpath, item.getProperty('stream'))
        #xbmc.executebuiltin(command)
        return True
    
    def to_s(self):
        size = self.size()
        s = 'Size: ' + str(size) + "\n"
        for i in range(0, size):
            s += '[' + str(i) + '] ' + self[i].getfilename() + ' / ' + self[i].getdescription() + "\n"
        return s

class QobuzPlayer(xbmc.Player):
    def __init__(self, type = xbmc.PLAYER_CORE_AUTO):
        super(QobuzPlayer, self).__init__()
        self.Playlist = QobuzPlayer_playlist( xbmc.PLAYLIST_MUSIC)
        self.id = None
        self.last_id = None
        self.Core = None
        self.startPlayingOn = None
        self.item = None
        self.playedTime = None
        self.watching = False
        self.PLAYER_TYPE = 'PAPLAYER'
        #xbmc.executebuiltin('PlayWith(DVDPLAYER)')
        
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
        
    def parse_pluginpath(self, path):
        info(self, "searchin in path: " + path)
        m = re.search('id=(\d+)', path)
        if not m:
            warn(self, "No id in playlist path: " + path)
            return None
        return m.group(1)
        
    def onPlayBackStopped(self):
        pass
    
    def prefetch_url(self, id):
        format = self.Core.Bootstrap.__addon__.getSetting('streamtype')
        if format == 'flac':
            format_id = 6
        elif format == 'mp3':
            format_id = 5
        else:
            warn(self, "Unknown format " + format + ", switching to FLAC")
            format_id = 6
        tu = self.Core.getTrackURL(id, format_id)
        #pprint.pprint(tu.get_data())
        return tu
    
    def set_item_stream_type(self, item, turl):
        url_data = turl.get_data()
        u = url_data['streaming_url']
        mimetype = 'audio/flac'
        if url_data['format_id'] == 6:
            xbmc.executebuiltin('PlayWith(PAPLAYER)')
            mimetype = 'audio/flac'
        if url_data['format_id'] == 5:
            xbmc.executebuiltin('PlayWith(DVDPLAYER)')
            mimetype = "audio/mpeg"
        info(self, "Set mimetype: " + mimetype)
        item.setProperty('mimetype', mimetype)
        b = self.Core.Bootstrap
        path = self.Core.Bootstrap.build_url(b.MODE, b.ID, b.POS)
        info(self, "rebuild path: " + path)
        item.setPath(path)
        item.setProperty('filename', path)
        item.setProperty('Path', path)
        item.setProperty('stream', u)
        item.setProperty("IsPlayable", "true")
        item.setProperty("Music", 'true')
        return item
    
    def prefetch_next_url(self, cpos):
        npos = self.Playlist.get_next_pos(cpos)
        if npos == -1:
            warn(self, "Cannot get valid playlist next index")
            return False
        if not self.Playlist.prefetching_needed(npos):
            info(self, "Next url is already resolved")
            return True
        id = self.parse_pluginpath(self.Playlist[npos].getfilename())
        if not id:
            warn(self, "Cannot parse playlist filename pos(" + str(npos))
            return False
        tu = self.prefetch_url(id)
        if not tu:
            warn(self, "Cannot fetch next url")
            return False
        t = QobuzTrack(self.Core, int(id))
        pprint.pprint(t)
        tag = QobuzTagTrack(self.Core, t.get_data())
        item = tag.getXbmcItem('player')
        t = self.set_item_stream_type(item, tu)
        self.Playlist.replace_path(npos, item)
        return True
    
    def play(self, id, pos):
        pos = int(pos)
        track = self.Core.getTrack(id)
        tag = QobuzTagTrack(self.Core, track.get_data())
        self.item = tag.getXbmcItem('player')
        b = self.Core.Bootstrap
        path = b.build_url(b.MODE, b.POS, b.POS)
        print "Setting path: " + path
#        self.item.setPath(path)
#        self.item.setProperty('path', path)
        self.cpos = pos #int(self.Core.Bootstrap.params['pos'])
        '''
            Prefetch current song streaming url
        '''
        url = None
        if self.Playlist.prefetching_needed(pos):
            tu = self.prefetch_url(id)
            if not tu:
                warn(self, 'Cannot fetch streaming url')
                return False
            url = ''
            try:
                url = tu.get_data()['streaming_url']
                self.item = self.set_item_stream_type(self.item, tu)
            except:
                warn(self, "Track don't have streaming url... aborting")
        else:
            url = self.Playlist[pos].getfilename()
        if not url:
            warn(self, "We don't have url to play track")
            return False
        else: self.item.setProperty('stream', url)
        if not self.item.getProperty('stream'):
            warn(self, "Non playable item: " + self.item.getLabel())
            self.Core.Bootstrap.GUI.showNotificationH('Qobuz Player', 'Track is not playable')
            return False
        '''
            PLaying track
        '''
        self.Core.Bootstrap.GUI.showNotificationH('Qobuz Player', 'Starting song')
        self.Playlist.replace_path(self.cpos, self.item)
        self.watching = False
        super(QobuzPlayer, self).playselected(self.cpos)
        xbmcplugin.setResolvedUrl(handle=self.Core.Bootstrap.__handle__,succeeded=True,listitem=self.item)
        #xbmc.executebuiltin('Dialog.Close(all,true)')
        #xbmc.executebuiltin('Container.Update("'+self.item.getProperty('Path')+'","'+self.item.getProperty('stream')+'")')
        #xbmc.executebuiltin('Control.SetFocus(-1,'+self.cpos+')')
        '''
            Waiting for song to start
        '''
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

        '''
            Watching playback
        '''
        self.watchPlayback()
        warn(self, 'stopping player for track: ' + self.item.getLabel())
        return True
    
    def set_track_id(self, id):
        if self.id:
            self.last_id = self.id
        self.id = id
    
            
    def watchPlayback( self):
        nextisresolved = False
        isNotified = False
        playedTime = None
        self.watching = True
        while self.isPlayingAudio():
            if not self.watching:
                warn('No more watching....')
                break
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
                if not nextisresolved:
                    ''' 
                    Prefetch next streaming url
                    '''
                    nextisresolved = self.prefetch_next_url(self.Playlist.getposition())
            if not isNotified and playedTime > 6:
                self.sendQobuzPlaybackStarted()
                isNotified = True
            if math.trunc(math.floor(playedTime)) % 5 == 0:
                info(self, 'Played time: ' + str(playedTime))
                #info(self, "Playlist:\n" + self.Playlist.to_s())
            xbmc.sleep(250)
        if playedTime > 6:
            self.sendQobuzPlaybackEnded(playedTime)
        
        info(self, "Stop watching playback (" + self.item.getLabel() + ' / ' + str(playedTime) + 's')
    
