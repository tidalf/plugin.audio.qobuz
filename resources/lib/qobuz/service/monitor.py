#     Copyright 2011 Stephen Denham, Joachim Basmaison, Cyril Leclerc
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

import os
import sys
from time import time
import xbmcaddon
import xbmcgui
import xbmc
import cPickle as pickle

pluginId = 'plugin.audio.qobuz'
__addon__ = xbmcaddon.Addon(id=pluginId)
__addonversion__ = __addon__.getAddonInfo('version')
__addonid__ = __addon__.getAddonInfo('id')
__cwd__ = __addon__.getAddonInfo('path')
dbg = True
addonDir = __addon__.getAddonInfo('path')
libDir = xbmc.translatePath(os.path.join(addonDir, 'resources', 'lib'))
qobuzDir = xbmc.translatePath(os.path.join(libDir, 'qobuz'))
sys.path.append(libDir)
sys.path.append(qobuzDir)

from exception import QobuzXbmcError
from bootstrap import QobuzBootstrap
from debug import warn, log
import qobuz
from util.file import FileUtil
from gui.util import containerRefresh, notifyH, getImage

class MyPlayer(xbmc.Player):
    def __init__(self, *args, **kwargs):
        xbmc.Player.__init__(self)
        self.locked = False
        self.lastId = None

    def onPlayBackEnded(self):
#        if not (self.track_id and self.total and self.elapsed):
#            return False
#        self.sendQobuzPlaybackEnded(
#            self.track_id, (self.total - self.elapsed) / 10)
        id  = xbmcgui.Window(10000).getProperty("NID")
        warn (self, "play back ended from monitor !!!!!!" + id)
        return True

    def onPlayBackStopped(self):
#        if not (self.track_id and self.total and self.elapsed):
#            return False
#        self.sendQobuzPlaybackEnded(
#            self.track_id, (self.total - self.elapsed) / 10)
        id  = xbmcgui.Window(10000).getProperty("NID")
        warn (self, "play back stopped from monitor !!!!!!" + id)
        return True
    
    def onPlayBackStarted(self):
        # workaroung bug, we are sometimes called multiple times.
        id  = xbmcgui.Window(10000).getProperty("NID")
        idToBeSend = id
        if not self.locked or self.lastId is not id: 
            self.locked = True
            warn (self, "play back started from monitor !!!!!!" + id )
            # wait 5s and if we're still playing the good song, send a start.
            xbmc.sleep(10000)
            if self.isPlayingAudio() and xbmcgui.Window(10000).getProperty("NID") == idToBeSend:
                qobuz.api.report_streaming_start(id)
            self.locked = False
            self.lastId = id
        return True
        
    def onQueueNextItem(self):
        id  = xbmcgui.Window(10000).getProperty("NID") 
        warn (self, "next item queued from monitor !!!!!!" + id )
        return True

class Monitor(xbmc.Monitor):

    def __init__(self, qobuz):
        super(Monitor, self).__init__()
        self.abortRequest = False
        self.last_garbage_on = time()
        self.garbage_refresh = 10
        
    def onAbortRequested(self):
        self.abortRequest = True

    def is_garbage_time(self):
        if time() > (self.last_garbage_on + self.garbage_refresh):
            return True
        return False
    
    def cache_remove_old(self, **ka):
        self.last_garbage_on = time()
        gData = {'limit': 1}
        if 'limit' in ka:
            gData['limit'] = ka['limit']
        """ function for deleting one file"""
        def delete_one(fileName, gData):
            data = None
            with open(fileName, 'rb') as f:
                f = open(fileName, 'rb')
                try:
                    data = pickle.load(f)
                except:
                    return False
                finally:
                    f.close()
            if not data or ((int(data['updatedOn']) + int(data['refresh'])) < time()):
                log("[QobuzCache]", (
                    "Removing old file: %s") % (repr(fileName)))
                try:
                    fu.unlink(fileName)
                    gData['limit'] -= 1
                except Exception as e:
                    warn("[QobuzCache]", ("Can't remove file %s\n%s")
                         % (repr(fileName), repr(e)))
                    return False
                if gData['limit'] <= 0:
                    return False
            return True
        fu = FileUtil()
        fu.find(qobuz.path.cache, '^.*\.dat$', delete_one, gData)
        return True

    def cache_remove_user_data(self):
        log(self, "Removing cached user data")
        try:
            if not qobuz.path.cache:
                raise QobuzXbmcError(who=self,
                                     what='qobuz_core_setting_not_set',
                                     additional='setting')
            fu = FileUtil()
            flist = fu.find(qobuz.path.cache, '^user.*\.dat$')
            for fileName in flist:
                    log(self, "Removing file " + fileName)
                    if not fu.unlink(fileName):
                        warn(self, "Failed to remove " + fileName)
            containerRefresh()
        except:
            warn(self, "Error while removing cached data")
            notifyH('Qobuz (i8n)',
                    'Failed to remove user data', getImage('icon-error-256'))
            return False
        return True

    def onSettingsChanged(self):
        self.cache_remove_user_data()


boot = QobuzBootstrap(__addon__, 0)
logLabel = '[QobuzCache]'
try:
    boot.bootstrap_app()
    monitor = Monitor(qobuz)
    player = MyPlayer()
    alive = True
    while alive:
        try:
            alive = not xbmc.abortRequested
        except:
            alive = False
        if not alive:
            break
        if monitor.is_garbage_time():
            log(logLabel, 'Periodic cleaning...')
            monitor.cache_remove_old(limit=20)
        xbmc.sleep(1000)
    log(logLabel, 'Exiting... bye!')
except QobuzXbmcError as e:
    warn('[' + pluginId + ']', "Exception while running plugin")
