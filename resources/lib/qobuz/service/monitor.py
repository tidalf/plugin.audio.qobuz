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
import xbmc
import cPickle as pickle

pluginId = 'plugin.audio.qobuz'
__addon__        = xbmcaddon.Addon(id=pluginId)
__addonversion__ = __addon__.getAddonInfo('version')
__addonid__      = __addon__.getAddonInfo('id')
__cwd__          = __addon__.getAddonInfo('path')
dbg = True
addonDir  = __addon__.getAddonInfo('path')
libDir = xbmc.translatePath(os.path.join(addonDir, 'resources', 'lib'))
qobuzDir = xbmc.translatePath(os.path.join(libDir, 'qobuz'))
sys.path.append(libDir)
sys.path.append(qobuzDir)

from exception import QobuzXbmcError
from bootstrap import QobuzBootstrap
from debug import warn
import qobuz
from util.file import FileUtil

class Monitor(xbmc.Monitor):
    
    def __init__(self, qobuz):
        super(Monitor, self).__init__()
        self.abortRequest = False
        self.last_garbage_on = time()
        self.garbage_refresh = 60
        
    def onAbortRequested(self):
        self.abortRequest = True
        
    def cache_remove_old(self, **ka):
        self.last_garbage_on = time()
        if not 'limit' in ka: ka['limit'] = 1
        try: 
            
            fu = FileUtil()
            flist = fu.find(qobuz.path.cache, '^.*\.dat$')
            count = 0
            for fileName in flist:
                data = None
                with open(fileName,'rb') as f:
                    f = open(fileName,'rb')
                    try:
                        data = pickle.load(f)
                    except: continue
                    finally: f.close()
                if  (data['updatedOn'] + data['refresh']) < time():
                    print "Removing old file: " + fileName
                    try:
                        fu.unlink(fileName)
                        count += 1
                        if count >= ka['limit']:
                            break
                    except Exception as e: 
                        warn(self, "Something went wrong while deleting: " + fileName + " / " + e.value)
            return True
        except: 
            warn(self, 'Something went wrong while trying to delete old cached file')
            return False
        return True
    
    def cache_remove_all(self):
        try:
            if not qobuz.path.cache:
                raise QobuzXbmcError(who=self, what='qobuz_core_setting_not_set', additional='setting')
            fu = FileUtil()
            flist = fu.find(qobuz.path.cache, '^user.*\.dat$')
            for fileName in flist:
                    fu.unlink(fileName)
            xbmc.executebuiltin('Container.Refresh')
        except: 
            warn(self, "Error while removing cached data")
            return False
        return True
    
    def onSettingsChanged(self):
        self.cache_remove_all()

boot = QobuzBootstrap(__addon__, 0)
try:
    boot.bootstrap_app()    
    monitor = Monitor(qobuz)
    while not xbmc.abortRequested:
        if time() > (monitor.last_garbage_on  + monitor.garbage_refresh):
            monitor.cache_remove_old(limit=10)
        xbmc.sleep(1000)
    
except QobuzXbmcError as e:
    warn('['+pluginId+']', "Exception while running plugin")


