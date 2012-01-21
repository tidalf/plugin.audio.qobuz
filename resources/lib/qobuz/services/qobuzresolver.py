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
from debug import *

boot = QobuzBootstrap(__addon__, 0)
boot.bootstrap_directories()
boot.bootstrap_lang()
boot.bootstrap_api()
boot.bootstrap_core()
boot.bootstrap_image()
boot.bootstrap_gui()

_sname_ = 'Qobuz Resolver'
__pid_file__ = 'qobuzresolver.pid'
__sleep__ = 5

from utils.pid import Pid
from services.cresolver import Service_url_resolver
        
service_name = 'Qobuz URL Resolver'

#def log(msg, lvl = xbmc.LOGDEBUG):
#    msg = service_name + ': ' + str(msg)
#    try:
#        xbmc.log(msg, lvl)
#    except:
#        print msg + "\n"
        

def gui_setting_enabled(pid):
    e = None
    try:
        e = qobuz.addon.getSetting('resolver_enabled')
    except:
        error(_sname_, "Cannot get addon setting...")
    if not e:
        info(_sname_, "We are not logged... Exiting!")
        return False
    elif e != 'true':
        info(_sname_, "Disabled from GUI settings... Exiting!")
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
    warn(_sname_, "Cannot setup player... exiting!")
    exit(1)
if not resolver.set_playlist():
    log(_sname_, "Cannot setup playlist... exiting!")
    warn(1)
    
def watcher():
    watch_retry = 3
    if not pid.can_i_run():
        warn(_sname_, "PID exists... exiting!")
        exit(0)
    if not pid.create():
        warn(_sname_, "Cannot create PID")
        exit(0)
    info(_sname_, "Starting")
    __timetowork__ = __sleep__
    run = True
    while (run):
        run = False
        try:
            run = not xbmc.abortRequested
        except:
            run = False
            warn(_sname_, "Cannot get xbmc.abortRequested value... exiting!")
            pid.remove()
            exit(0)
        if not run:
            debug(_sname_, "Not running removing pid")
            pid.remove()
            exit(0)
        if not gui_setting_enabled(pid):
            info(_sname_, "Disabled from GUI... exiting!")
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
                warn(_sname_, "Cannot resolve track!")
        except ServiceError as e:
            if e.arg == 'login':
                warn(_sname_, "Login error...abort!")
                run = False
        except:
            warn(_sname_, "Resolver fail to watch playlist!")
        if not pid.touch():
            log(_sname_, 'Cannot touch pid file: ' + pid.file)
        else:
            debug(_sname_, 'Touching pid file: ' + pid.file)
    if not pid.remove():
        warn(_sname_, "Cannot remove pid file: " + pid.file)
    info(_sname_, "Exiting...")

'''
    MAIN
'''
#atexit.register(pid.remove)
if __name__ == "__main__":
    if not gui_setting_enabled(pid):
        exit(0)
    watcher()
        
    
