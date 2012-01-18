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
import os
import sys
import time
import re
import atexit
import xbmcaddon
import xbmc
import signal

__addon_name__   = 'plugin.audio.qobuz'
__addon_url__    = 'plugin://' + __addon_name__ + '/'
__addon__        = xbmcaddon.Addon(id=__addon_name__)
__addonversion__ = __addon__.getAddonInfo('version')
__addonid__      = __addon__.getAddonInfo('id')
__cwd__          = __addon__.getAddonInfo('path')

addonDir  = __addon__.getAddonInfo('path')
libDir = xbmc.translatePath(os.path.join(addonDir, 'resources', 'lib'))
qobuzDir = xbmc.translatePath(os.path.join(libDir, 'qobuz'))
sys.path.append(libDir)
sys.path.append(qobuzDir)
import qobuz
from bootstrap import QobuzBootstrap
boot = QobuzBootstrap(__addon__, 0)
boot.bootstrap_directories()
boot.bootstrap_lang()
boot.bootstrap_api()
boot.bootstrap_core()

__pid_file__ = 'qobuzresolver.pid'
__sleep__ = 5

from utils.tag import QobuzTagTrack
from data.track import QobuzTrack
from utils.pid import Pid
from services.cresolver import Service_url_resolver
        
service_name = 'Qobuz URL Resolver'

def log(msg, lvl = xbmc.LOGNOTICE):
    msg = service_name + ': ' + str(msg)
    try:
        xbmc.log(msg, lvl)
    except:
        print msg + "\n"
        

def gui_setting_enabled(pid):
    e = None
    try:
        e = qobuz.addon.getSetting('resolver_enabled')
    except:
        print "Cannot get addon setting..."
    if not e:
        log("We are not logged... Exiting!")
        return False
    elif e != 'true':
        log("Disabled from GUI settings... Exiting!")
        return False
    return True

'''
    Our watcher infinite loop
    We are put all our work in a try/catch block so our have
    lesser chance to die. Pid file is not unlinked on crash ...
    TODO: If plugin has never been launched cache path doesn't exist,
    our pid file can't be created, our service die ...
'''
'''
    MAIN
'''
pid_path = os.path.join(qobuz.path.cache, __pid_file__)
pid_id =  os.getpid()
pid = Pid(pid_path, pid_id)
pid.set_old_pid_age(__sleep__ * 5)
resolver = Service_url_resolver()

if not resolver.set_player():
    print "Cannot setup player... exiting!"
    exit(1)
if not resolver.set_playlist():
    print "Cannot setup playlist... exiting!"
    exit(1)
    
def watcher():
    watch_retry = 3
    if not pid.can_i_run():
        log("PID exists... exiting!")
        exit(0)
    if not pid.create():
        log("Cannot create PID")
        exit(0)
    log("Starting")
    __timetowork__ = __sleep__
    run = True
    while (run):
        run = False
        try:
            run = not xbmc.abortRequested
        except:
            run = False
            log("Cannot get xbmc.abortRequested value... exiting!")
            pid.remove()
            exit(0)
        if not run:
            log("Not running removing pid")
            pid.remove()
            exit(0)
        if not gui_setting_enabled(pid):
            log("Disabled from GUI... exiting!")
            pid.remove()
            exit(0)
        if __timetowork__ > 0:
            __timetowork__-=1
            time.sleep(1)
            continue
        else:
            __timetowork__ = __sleep__
        try:
            if not resolver.watch():
                print "Cannot resolve track!"
            else:
                print "Track resolved"
        except:
            log("Resolver fail to watch playlist!")
        if not pid.touch():
            log('Cannot touch pid file: ' + pid.file)
        else:
            log('Touching pid file: ' + pid.file)
    if not pid.remove():
        log("Cannot remove pid file: " + pid.file)
    log("Exiting...")


#atexit.register(pid.remove)

if __name__ == "__main__":
    if not gui_setting_enabled(pid):
        exit(0)
    watcher()
        
    
