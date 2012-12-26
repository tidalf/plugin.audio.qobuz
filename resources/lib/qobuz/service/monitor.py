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
import xbmcaddon
import xbmc

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
from debug import log
import qobuz

class Monitor(xbmc.Monitor):
    def __init__(self, qobuz):
        super(Monitor, self).__init__()
        

    def onSettingsChanged(self):
        log(self, 'Addong settings has changed')
        qobuz.registry.delete(name='user')
        qobuz.registry.delete(name='user-playlists')
        qobuz.registry.delete(name='user-playlist-id')
        #qobuz.registry.delete(name='user-playlist') #@TODO Delete all user playlist (or not :p)
        xbmc.executebuiltin('Container.Refresh')

boot = QobuzBootstrap(__addon__, 0)
try:
    boot.bootstrap_app()    
    monitor = Monitor(qobuz)
    while (not xbmc.abortRequested):
        xbmc.sleep(1000)
    
except QobuzXbmcError as e:
    warn('['+pluginId+']', "Exception while running plugin")


