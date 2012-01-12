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
#import threading
import math
import pprint

import xbmc
import xbmcplugin
import xbmcgui

from debug import info, warn, log
from data.track import QobuzTrack
from utils.tag import QobuzTagTrack
from data.track_streamurl import QobuzTrackURL
from utils.icacheable import ICacheable

class QobuzPlaylist(ICacheable):

    def __init__(self, Core):
        self.Core = Core
        super(QobuzPlaylist, self).__init__( self.Core.Bootstrap.cacheDir, 
                                          'player-playlist')
        self.set_cache_refresh(36000)
        info(self, "Cache duration: " + str(self.cache_refresh))
        self._raw_data = []
        self.load()
        
    def add(self, url, item, id):
        data = self.get_raw_data()
        pos = len(data) - 1
        #print "Add track " + str(id) + "[" + str(pos) + "]\n"
        self.get_raw_data().append({
                         'id': id,
                         'url': url,
                         'index': pos,
        })
        return pos
    
    def load(self):
        print "Load playlist data"
        self.set_raw_data(self._load_cache_data())
    
    def save(self):
        print "Save playlist data"
        self._save_cache_data(self.get_raw_data())

    def get_id(self, id):
        print "Search id: " + str(id)
        data = self.get_raw_data()
        if not data:
            warn(self, "No playlist data, cannot get item with id")
            return None
        l = len(data)
        if l < 1:
            warn(self, "PLaylist is empty, cannot get item with id")
            return None
        for t in data:
            if t['id'] == id:
                return t
        return None
        
    def get_position(self, pos):
        data = self.get_raw_data()
        if not data:
            warn(self, "No playlist data, cannot get item with position")
            return None
        l = len(data)
        if l < 1:
            warn(self, "PLaylist is empty, cannot get item with position")
            return None
        if pos >= l:
            warn(self, "Playlist index out of bound (> size)")
            return None
        return data[pos]
    
    def _fetch_data(self):
        return self._raw_data
    
    def clear(self):
        self.set_raw_data([])
        if not self.delete_cache():
            print "Saving empty array..."
            if not self.save():
                print "Cannot clear playlist"
   
    def resolve_url_at_pos(self, pos): 
        t = self.get_position(pos)
        if not t:
            warn(self, "No item in playlist at position " + pos)
            return None
        if 'url_resolved' in t:
            return t
        format = self.Core.Bootstrap.__addon__.getSetting('streamtype')
        if format == 'flac':
            format_id = 6
        elif format == 'mp3':
            format_id = 5
        else:
            warn(self, "Unknown stream format from settings...")
            format_id = 6
        turl = QobuzTrackURL(self.Core, t['id'], format_id)
        data = turl.get_data()
        if not data:
            warn(self, "Cannot resolve url for track id: " + str(t['id']))
            return None
        pprint.pprint(data)
        #exit(1)
        t['streaming_url'] = data['streaming_url']
        t['streaming_type'] = data['streaming_type']
        t['format_id'] = data['format_id']
        if int(data['format_id']) == 6:
            t['format_name'] = 'flac'
            t['mimetype'] = 'audio/flac'
        else:
            t['format_name'] = 'mp3'
            t['mimetype'] = 'audio/mpeg'
#        t['mimetype'] = 'audio/mpeg'
        t['request_format_id'] = format_id
        t['request_format_type'] = format
        print "Set resolved to : " + t['streaming_url']
        return t
            
    def to_s(self):
        s = ''
        #pprint.pprint(self.get_data())
        for t in self.get_data():
            s += 'Track[' + t['id'] + "] " + t['url'] + "\n"
        return s

class QobuzPlayer_playlist(xbmc.PlayList):
    def __init__(self, type = xbmc.PLAYLIST_MUSIC):
        super(QobuzPlayer_playlist, self).__init__()
        self.Core = None
        self.data = None
        
    def setCore(self, Core):
        self.Core = Core
        self.data = QobuzPlaylist(self.Core)
    
    def get_id(self, id):
        return self.data.get_id(id)
        
    def add(self, url, item, id):
        index = self.data.add(url, item, id)
        super(QobuzPlayer_playlist, self).add(url, item, index)
    
    def save(self):
        self.data.save()
    
    def load(self):
        self.data.load()
        
    def clear(self):
        super(QobuzPlayer_playlist, self).clear()
        self.data.clear()
        
#    def getCurrentPos(self, item):
#        cpath = item.getProperty('path')
#        cstream = item.getProperty('stream')
#        print "CPATH: " + cpath
#        print "CSTREAM: " + cstream 
#        size  =  self.size()
#        cpos = -1
#        for i in range(0, size):
#            filename =  self[i].getfilename()   
#            print "MATCH: " + filename   
#            if cpath == filename:
#                cpos = i
#                break
#            elif cstream == filename:
#                cpos = i
#                break
#        print "Current position: " + str(cpos)
#        return cpos
#    
    def is_valid_position(self, cpos):
        if cpos < 0:
            warn(self, "Playlist index < 0")
            return False
        if cpos >= self.size():
            warn(self, "Playlist index > 0")
            return False
        try:
            test = self[cpos]
            return True
        except: return False
    
#    def prefetching_needed(self, pos):
#        if not self.is_valid_position(pos):
#            warn(self, "Playlist positon is not valid: " + str(pos))
#            return False
#        if 'http://' in self[pos].getfilename():
#            info(self, 'URL is already resolved')
#            return False
#        info(self, "Need to prefetch playlist item at index: " + str(pos))
#        return True
        
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

    def resolve_url_at_pos(self, pos):
        t = self.data.resolve_url_at_pos(pos)
        if not t:
            warn(self, "Cannot resolve url at position: " + str(pos))
            return None
        pt = None 
        try:
            pt = self[pos]
        except:
            warn(self, "Cannnot get track at position " + str(pos))
            return None
        track = QobuzTrack(self.Core, t['id'])
        if not track:
            warn(self, "Cannot get QobuzTrack with id: " + str(t['id']))
            return None
        tag = QobuzTagTrack(self.Core, track.get_data())
        item = tag.getXbmcItem('player')
        item.setProperty('url', t['url'], )
        item.setProperty('streaming_url', t['streaming_url'])
        item.setProperty('mimetype', t['mimetype'])
        item.setProperty('IsPlayable', 'true')
        item.setProperty('Music', 'true')
        
        self.replace_path(pos, item)
        print self.to_s()
        return item
        
        
    def replace_path(self, cpos, item):
        if not self.is_valid_position(cpos):
            warn(self, "Cannot replace url (index out of bound)")
            return False
        cpath = self[cpos].getfilename()
        if not cpath:
            warn(self, 'Current path is empty, abort')
            return False
        if not cpath.startswith('plugin://'): 
            print "We already have correct url in playlist... abort"
            return True
        item.setPath(cpath)
        print "Path replace: " + item.getProperty('path')
        item.setPath(item.getProperty('streaming_url'))
#        newitem = xbmcgui.ListItem(item.getProperty('path'), '', '', path=item.getProperty('streaming_url'))
        self.remove(cpath)
        super(QobuzPlayer_playlist, self).add(url=item.getProperty('streaming_url'), listitem=item, index=cpos)
        command = 'Container.update("%s","%s")' % ( cpath, item.getProperty('streaming_url'))
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
        self.Playlist = None
        self.id = None
        self.last_id = None
        self.Core = None
        self.startPlayingOn = None
        self.item = None
        self.playedTime = None
        self.watching = False
        self.PLAYER_TYPE = 'PAPLAYER'
        #xbmc.executebuiltin('PlayWith(DVDPLAYER)')
        
    def setCore (self, Core):
        self.Core = Core
        self.Playlist = QobuzPlayer_playlist( xbmc.PLAYLIST_MUSIC)
        self.Playlist.setCore(Core)
        
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
        
#    def parse_pluginpath(self, path):
#        info(self, "searchin in path: " + path)
#        m = re.search('id=(\d+)', path)
#        if not m:
#            warn(self, "No id in playlist path: " + path)
#            return None
#        return m.group(1)
        
#    def onPlayBackStopped(self):
#        pass
    
#    def prefetch_url(self, id):
#        format = self.Core.Bootstrap.__addon__.getSetting('streamtype')
#        if format == 'flac':
#            format_id = 6
#        elif format == 'mp3':
#            format_id = 5
#        else:
#            warn(self, "Unknown format " + format + ", switching to FLAC")
#            format_id = 6
#        tu = self.Core.getTrackURL(id, format_id)
#        #pprint.pprint(tu.get_data())
#        return tu
    
#    def set_item_stream_type(self, item, turl):
#        url_data = turl.get_data()
#        u = url_data['streaming_url']
#        mimetype = 'audio/flac'
#        if url_data['format_id'] == 6:
#            xbmc.executebuiltin('PlayWith(PAPLAYER)')
#            mimetype = 'audio/flac'
#        if url_data['format_id'] == 5:
#            xbmc.executebuiltin('PlayWith(DVDPLAYER)')
#            mimetype = "audio/mpeg"
#        info(self, "Set mimetype: " + mimetype)
#        item.setProperty('mimetype', mimetype)
#        b = self.Core.Bootstrap
#        path = self.Core.Bootstrap.build_url(b.MODE, b.ID, b.POS)
#        info(self, "rebuild path: " + path)
#        item.setPath(path)
#        item.setProperty('filename', path)
#        item.setProperty('Path', path)
#        item.setProperty('stream', u)
#        item.setProperty("IsPlayable", "true")
#        item.setProperty("Music", 'true')
#        return item
    
#    def prefetch_next_url(self, cpos):
#        npos = self.Playlist.get_next_pos(cpos)
#        if npos == -1:
#            warn(self, "Cannot get valid playlist next index")
#            return False
#        if not self.Playlist.prefetching_needed(npos):
#            info(self, "Next url is already resolved")
#            return True
#        id = self.parse_pluginpath(self.Playlist[npos].getfilename())
#        if not id:
#            warn(self, "Cannot parse playlist filename pos(" + str(npos))
#            return False
#        tu = self.prefetch_url(id)
#        if not tu:
#            warn(self, "Cannot fetch next url")
#            return False
#        t = QobuzTrack(self.Core, int(id))
#        pprint.pprint(t)
#        tag = QobuzTagTrack(self.Core, t.get_data())
#        item = tag.getXbmcItem('player')
#        t = self.set_item_stream_type(item, tu)
#        self.Playlist.replace_path(npos, item)
#        return True
#    
#    def skipsample(self, tag, pos):
#        skip = self.Core.Bootstrap.getSetting('skipsample')
#        if skip == 'true': skip = True
#        else: skip = False
#        if tag['streaming_type'] != 'full' and skip:
#            return self.Playlist.get_next_pos(pos)
#        return pos
#    
#    def get_track(self, id):
#        track = self.Core.getTrack(id)
#        tag = QobuzTagTrack(self.Core, track.get_data())
#        return (track, tag)
            
    def play(self, id, pos):
        pos = int(pos)
        #self.data.load()
        print "PLaylist data"
        #self.Playlist.data.load()
        #print self.Playlist.data.to_s()
        plt = self.Playlist.get_id(id)
        if plt:
            print "url: " + plt['url']
        else:
            warn(self, "Track not found [" + str(id) + "]")
            return False
        print "Track id: " + str(plt['id']) + ' at position ' + str(plt['index'])
        self.cpos = int(plt['index'])
        self.item = self.Playlist.resolve_url_at_pos(plt['index'])
        if not self.item:
            warn(self, "Could not play track with id " + str(id))
            return False
        '''
            PLaying track
        '''
        self.Core.Bootstrap.GUI.showNotificationH('Qobuz Player', 'Starting song')
        self.watching = False
        print "Playing track number: " + str(self.cpos)
#        super(QobuzPlayer, self).playselected(self.cpos)
        print "URl: " + self.item.getProperty('streaming_url')
        print "Filename: " + self.Playlist[self.cpos].getfilename()
        print self.Playlist.to_s()
        super(QobuzPlayer, self).play(self.item.getProperty('streaming_url'))
        xbmcplugin.setResolvedUrl(handle=self.Core.Bootstrap.__handle__,succeeded=True,listitem=self.item)
        return
        #xbmc.executebuiltin('Dialog.Close(all,true)')
        #xbmc.executebuiltin('Container.Update("'+self.item.getProperty('Path')+'","'+self.item.getProperty('stream')+'")')
        #xbmc.executebuiltin('Control.SetFocus('+str(self.cpos)+')')
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
            return False
        #self.set_track_id(self.Core.Bootstrap.ID)
        print "Playing file: " + self.getPlayingFile()
        print "Description: " + self.Playlist[self.Playlist.getposition()].getdescription()

        '''
            Watching playback
        '''
        self.watchPlayback()
        warn(self, 'stopping player for track: ' + self.item.getLabel())
        return True
    
#    def set_track_id(self, id):
#        if self.id:
#            self.last_id = self.id
#        self.id = id
    
            
    def watchPlayback( self):
        nextisresolved = False
        isNotified = False
        playedTime = 0
        previousTime = 0
        self.watching = True
        pos = self.cpos
        while self.isPlayingAudio(): 
            try:
                if playedTime:
                    previousTime = playedTime
                playedTime = self.getTime()
            except:
                warn(self, "Cannot getTime(), player may be not running") 
            timeleft = None
            if playedTime:
                if previousTime:
                    if playedTime < previousTime:
                        print "Track Changed"
                        playedTime = 0
                        previousTime = 0
                        nextisresolved = False
                        isNotified = False
                        pos = self.Playlist.get_next_pos(pos)
                try:
                    timeleft = self.getTotalTime() - playedTime
                except:
                    warn(self, "Cannot getTotalTime(), player may be not running")
            if (timeleft != None) and (timeleft < 20):
                if not nextisresolved:
                    ''' 
                    Prefetch next streaming url
                    '''
                    npos = self.Playlist.get_next_pos(pos)
                    item = self.Playlist.resolve_url_at_pos(npos)
                    if item:
                        self.Core.Bootstrap.GUI.showNotificationH('Qobuz Player', 'Next Song: ' + item.getLabel())
                        nextisresolved = True
                    #nextisresolved = self.prefetch_next_url(self.Playlist.getposition())
                    pass
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
    
