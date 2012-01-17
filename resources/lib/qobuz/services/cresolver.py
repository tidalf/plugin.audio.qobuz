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

import xbmc
import re

from utils.pid import Pid
from utils.list_item import QobuzListItem_track
import qobuz

class Service_url_resolver():
    
    def __init__(self):
        self.player = None
        self.playlist = None
#        self.pid = Pid(pid_path, pid_id)
#        self.pid.set_old_pid_age(sleep)
        self.last_track_number = None
        self.retry_max = 3
        self.retry = 3
        self.need_resolve_startswith = 'plugin://plugin.audio.qobuz/'
        self.streaming_format = None
        self.set_streaming_format()
        
    def set_streaming_format(self):
        try:
            self.streaming_format = qobuz.addon.getSetting('streamtype')
        except:
            print "Cannot set streaming format"
            return False
        return True
        
    def set_player(self):
        try:
            self.player = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
        except:
            print "Cannot set player!"
            return False
        return True
            
    def set_playlist(self):
        try:
            self.playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
        except:
            print "Cannot set playlist!"
            return False
        return True

    def is_playing(self):
        ret = False
        try:
            ret = self.player.isPlayingAudio()
        except:
            print "Exception: Cannot determine if we're playing audio\n"
        return ret
    
    def get_playing_song_position(self):
        ret = None
        try:
            ret = self.playlist.getposition()
        except:
            print "Cannot get current track playing position\n"
        return ret
    
    def get_next_position(self, pos):
        newpos = pos + 1
        try:
            pos = self.playlist[newpos]
        except:
            return None
        return newpos
    
    def position_need_resolve(self, pos):
        item = None
        try:
            item = self.playlist[pos]
        except:
            print "Cannot get playlist item at position " + str(pos)
            return None
        name = None
        try:
            name = item.getfilename()
        except:
            print "Cannot get filename for item at position " + str(pos)
        if name.startswith(self.need_resolve_startswith):
            return True
        return False
    
    def get_id_from_filename(self, file):
        print "Try to extract id from: " + file
        match = re.search('^'+self.need_resolve_startswith+'?.*id=(\d+).*$', file)
        if not match:
            return None
        return match.group(1)
        
    def replace_playlist_path(self, pos, item):
        i = None
        try:
            i = self.playlist[pos]
        except:
            print "Invalid playlist position! " + str(i)
            return False
        cpath = None
        try:
            cpath = self.playlist[pos].getfilename()
        except:
            print "Cannot get playlist filename"
            return False
        if not cpath.startswith(self.need_resolve_startswith):
            print "Don't need to resolve this path: " + cpath
            return False
        item.setPath(item.getProperty('streaming_url'))
        try:
            self.playlist.remove(cpath)
        except:
            print "Cannot remove path from playlist: " + cpath
            return False
        try:
            self.playlist.add(url=item.getProperty('streaming_url'), listitem=item, index=pos)
        except:
            print "Cannot add item to current playlist"
            return False
        return True
    
    def get_item_at_pos(self, pos):
        item = None
        try:
            item = self.playlist[pos]
        except:
            print "Cannot get item at position " + str(pos)
            return None
        return item
    
    def get_playlist_size(self):
        size = 0
        try:
            size = self.playlist.size()
        except:
            print "Cannot get playlist size"
            return None
        return size
    
    def do_we_try_resolve(self, pos):
        if pos != self.last_track_number:
            self.retry = 3
            return True
        if self.retry > 0:
            print "We are trying again to resolve this item:" + str(self.retry)
            self.retry -= 1
            return True
        print "We have reached maximum retry, can't resolve next track"
        return False
        
    def watch(self):
        size = self.get_playlist_size()
        if size == None:
            return False
        cposition = self.get_playing_song_position()
        if cposition == None:
            return False
        if self.last_track_number == None:
            self.last_track_number = cposition
        nposition = self.get_next_position(cposition)
        if nposition == None:
            return False
        if not self.do_we_try_resolve(nposition):
            print "We dont try to resolve this position again"
            return False
        if not self.position_need_resolve(nposition):
            print "Don't need to resolve this position"
            return True
        pl_item = self.get_item_at_pos(nposition)
        if not pl_item:
            return False
        id = None
        try:
            id = self.get_id_from_filename(pl_item.getfilename())
        except:
            print "Cannot extract id from filename item"
            return False
        if not id:
            print "No track id"
            return False
        q_item = None
        try:
            q_item = QobuzListItem_track(id)
        except:
            print "Cannot get QobuzListItem"
            return False
        try:
            q_item.fetch_stream_url(self.streaming_format)
        except:
            print "Cannot fetch streaming url"
            return False
        x_item = None
        try:
            x_item = q_item.get_xbmc_list_item()
        except:
            print "Cannot get xbmc item"
            return False
        if not self.replace_playlist_path(nposition, x_item):
            print "Cannot replace item in playlist"
        print "Item replaced"
        return True
        
        
        
        
        
            
        