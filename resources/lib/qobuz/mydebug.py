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
#     along with xbmc-qobuz.   If not, see <http://www.gnu.org/licenses/>..
import os

import xbmc
import xbmcaddon

from utils import _sc

__debugging__ = False
if xbmcaddon.Addon(id='plugin.audio.qobuz').getSetting('debug') == 'true':
    __debugging__ = True
    print "Debug IS ON"

###############################################################################
# Logging helper functions
###############################################################################
def log(obj,msg, lvl = xbmc.LOGDEBUG):
    name = None
    try:
        name = obj.__class__.__name__
    except:
        name = type(obj)
    xbmc.log(_sc('[' + str(name) + "] " + msg), lvl)

def warn(obj,msg):
    if __debugging__:
        log(obj,msg, xbmc.LOGERROR)

def info(obj,msg):
    if __debugging__:
        log(obj,msg, xbmc.LOGNOTICE)

def error(obj,msg,code):
    log(obj,msg,'ERROR')
    os.sys.exit(code)