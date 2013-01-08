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
from gui.util import containerRefresh, notifyH, getImage, executeBuiltin
from node.track import Node_track
from api import api
import threading

keyTrackId = 'QobuzPlayerTrackId'
keyMonitoredTrackId = 'QobuzPlayerMonitoredTrackId'

class MyPlayer(xbmc.Player):
    def __init__(self, *args, **kwargs):
        xbmc.Player.__init__(self)
        self.lastId = None
        self.lock = threading.Lock()

    def getProperty(self, key):
        """Wrapper to retrieve property from Xbmc Main Window
            Parameter:
                key: string, property that you want to get
            * Lock may be useless ...
        """
        try:
            if not self.lock.acquire(5):
                warn(self, "getProperty: Cannot acquire lock!")
                return ''
            return xbmcgui.Window(10000).getProperty(key)
        finally:
            self.lock.release()

    def setProperty(self, key, value):
        """Wrapper to set Xbmc Main window property
            Parameter:
                key: string, property name to set
                value: string, value to set
        """
        try:
            if not self.lock.acquire(5):
                warn(self, "setProperty: Cannot acquire lock!")
                return
            xbmcgui.Window(10000).setProperty(key, value)
        finally:
            self.lock.release()

    def onPlayBackEnded(self):
        nid  = self.getProperty(keyTrackId)
        warn (self, "play back ended from monitor !!!!!!" + nid)
        return True

    def onPlayBackStopped(self):
        nid  = self.getProperty(keyTrackId)
        warn (self, "play back stopped from monitor !!!!!!" + nid)
        return True

    def onPlayBackStarted(self):
        # workaroung bug, we are sometimes called multiple times.
        mid = self.getProperty(keyMonitoredTrackId)
        if mid:
            warn(self, "Already monitoring song id: %s" % (mid)) 
            return False
        nid  = self.getProperty(keyTrackId)
        if not nid:
            warn(self, "No track id set by the player...")
            return False
        self.setProperty(keyMonitoredTrackId, nid)
        idToBeSend = nid
        log(self, "play back started from monitor !!!!!!" + nid )
        xbmc.sleep(10000)
        if self.isPlayingAudio() and self.getProperty(keyTrackId) == idToBeSend:
            self.setProperty(keyMonitoredTrackId, '')
            api.track_resportStreamingStart(nid)
        return True

    def onQueueNextItem(self):
        nid  = self.getProperty(keyTrackId) 
        warn (self, "next item queued from monitor !!!!!!" + nid )
        return True

class Monitor(xbmc.Monitor):

    def __init__(self, qobuz):
        super(Monitor, self).__init__()
        self.abortRequested = False
        self.garbage_refresh = 60 * 5
        self.last_garbage_on = time() - (self.garbage_refresh + 1)
        self.Player = MyPlayer()
        
    def onAbortRequested(self):
        self.abortRequested = True
        print "Abort requested"

    def is_garbage_time(self):
        if time() > (self.last_garbage_on + self.garbage_refresh):
            return True
        return False

    def isIdle(self, since = 1):
        try:
            if xbmc.getGlobalIdleTime() >= since:
                return True
            return False
        except:
            return False

    def cache_remove_old(self, **ka):
        timeStarted = time()
        self.last_garbage_on = time()
        gData = {'limit': 1, 'count': 0}
        if 'limit' in ka:
            gData['limit'] = ka['limit']
        """Callback deleting one file
        """
        def delete_one(fileName, gData):
            gData['count'] += 1
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
                log("QobuzCache", (
                    "Removing old file: %s") % (repr(fileName)))
                try:
                    fu.unlink(fileName)
                    gData['limit'] -= 1
                except Exception as e:
                    warn("QobuzCache", ("Can't remove file %s\n%s")
                         % (repr(fileName), repr(e)))
                    return False
                if gData['limit'] <= 0:
                    return False
            return True
        fu = FileUtil()
        fu.find(qobuz.path.cache, '^.*\.dat$', delete_one, gData)
        log(self, "%s cached file(s) checked in %2.1s s" % (str(gData['count']), 
            str(time() - timeStarted) ))
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
            executeBuiltin(containerRefresh())
        except:
            warn(self, "Error while removing cached data")
            notifyH('Qobuz (i8n)',
                    'Failed to remove user data', getImage('icon-error-256'))
            return False
        return True

    def onSettingsChanged(self):
        self.cache_remove_user_data()

boot = QobuzBootstrap(__addon__, 0)
logLabel = 'QobuzMonitor'
try:
    boot.bootstrap_app()
    monitor = Monitor(qobuz)
    alive = True
    while alive:
        alive = False
        try:
            alive = not monitor.abortRequested
        except Exception as e:
            print "Exception while getting abortRequested..."
            raise e
        if not alive:
            break
        if monitor.isIdle(60) and monitor.is_garbage_time():
            log(logLabel, 'Periodic cleaning...')
            monitor.cache_remove_old(limit=20)
        xbmc.sleep(1000)
    print '[%s] Exiting... bye!' % (logLabel)
except:
    print '[%s] Exiting monitor' % (pluginId)
