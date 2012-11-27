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
import time
import re
import math
import pprint

import xbmc
import xbmcplugin
import xbmcgui
import json
import qobuz
from debug import info, warn, debug
from gui.progress import Progress

from node.track import Node_track

class QobuzPlayer(xbmc.Player):

    def __init__(self, type = xbmc.PLAYER_CORE_AUTO):
        super(QobuzPlayer, self).__init__()
        self.track_id = None
        self.total = None
        self.elapsed = None

    def sendQobuzPlaybackEnded(self, track_id, duration):
        qobuz.api.report_streaming_stop(track_id, duration)

    def sendQobuzPlaybackStarted(self, track_id):
        qobuz.api.report_streaming_start(track_id)

    def onPlayBackEnded(self):
        if not (self.track_id and self.total and self.elapsed):
            return False
        self.sendQobuzPlaybackEnded(self.track_id, (self.total - self.elapsed) / 10)
        return True
    
    def OnQueueNextItem(self):
        return True
    
    def onPlayBackStopped(self):
        if not (self.track_id and self.total and self.elapsed):
            return False
        self.sendQobuzPlaybackEnded(self.track_id, (self.total - self.elapsed) / 10)
        return True

    def play(self, id):
#        progress = Progress(True)
#        progress.create("Qobuz Player")
        debug(self, "Playing track: " + str(id))
        node = Node_track()
        node.set_id(id)
        node.set_cache()
        data = node.cache.fetch_data()
        label = None
        item = None
        if not data:
            warn(self, "Cannot get track data")
            label = "Maybe an invalid track id"
            item = xbmcgui.ListItem("No track information",
                                '',
                                '',
                                '',
                                '')
        else:
            node.set_data(data)
            item = node.make_XbmcListItem()
        lang = qobuz.lang
        mimetype = node.get_mimetype()
        if not mimetype:
            warn(self, "Cannot get track stream url")
            return False
        item.setProperty('mimetype', mimetype)
        streaming_url = node.get_streaming_url()
        # some tracks are not authorized for stream and a 60s sample is returned, in that case we overwrite the song duration
        if node.is_sample(): 
            item.setInfo('music', infoLabels = {
                                   'duration': 60,
                                   } )
            # don't warn for free account (all songs except purchases are 60s limited)
            if not qobuz.gui.is_free_account():
                qobuz.gui.notifyH("Qobuz", "Sample returned") 
        item.setPath(streaming_url)
        watchPlayback = False
        '''
            PLaying track
        '''
        if qobuz.addon.getSetting('notification_playingsong') == 'true':
            qobuz.gui.notifyH(lang(34000), node.get_label().encode('utf8', 'replace'), node.get_image())

        '''
            We are called from playlist...
        '''

        if qobuz.boot.handle == -1:
            super(QobuzPlayer, self).play(streaming_url, item, False)
        else:
            xbmcplugin.setResolvedUrl(handle = qobuz.boot.handle, succeeded = True, listitem = item)
        '''
            May be a bad idea!!!
        '''
        #xbmc.executebuiltin('Dialog.Close(all,true)')
        '''
            Waiting for song to start
        '''
        timeout = 10
        debug(self, "Waiting song to start")
        while timeout > 0:
            if not self.isPlayingAudio() or self.getPlayingFile() != streaming_url:
                xbmc.sleep(250)
                timeout -= 0.250
            else:
                break
        if timeout <= 0:
            warn(self, "Player can't play track: " + item.getLabel())
#            progress.update(100, "Cannot play track:", node.get_label())
#            progress.close()
            return False
#        progress.update(100, "Playing track", node.get_label())
#        progress.close()
        return self.watch_playing(node, streaming_url)

    def isPlayingAudio(self):
        try: return super(QobuzPlayer, self).isPlayingAudio()
        except: warn(self, "EXCEPTION: isPlayingAudio")
        return False

    def getPlayingFile(self):
        try: return super(QobuzPlayer, self).getPlayingFile()
        except: warn(self, "EXCEPTION: getPlayingFile")
        return ''

    def getTotalTime(self):
        try: return super(QobuzPlayer, self).getTotalTime()
        except: warn(self, "EXCEPTION: getTotalTime")
        return -1

    def watch_playing(self, node, streaming_url):
        start = None
        self.total = None
        self.elapsed = None
        self.track_id = node.get_id()
        self.total = self.getTotalTime()
        while self.isPlayingAudio() and self.getPlayingFile() == streaming_url:
            self.elapsed = self.getTime()
            if not start and self.elapsed >= 5:
                self.sendQobuzPlaybackStarted(node.get_id())
                start = True
            xbmc.sleep(500)
        return True
