# Copyright 2011 Joachim Basmaison, Cyril Leclerc

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
from utils import _sc
import os
__debugging__ = 1

###############################################################################
# Loggin helper functions
###############################################################################
def log(obj,msg,lvl="LOG"):
    print(_sc('[' + lvl + '] ' + str(type(obj)) + ": " + msg))

def warn(obj,msg):
    if __debugging__:
        log(obj,msg,'WARN')

def info(obj,msg):
    if __debugging__:
        log(obj,msg,'INFO')

def error(obj,msg,code):
    log(obj,msg,'ERROR')
    os.sys.exit(code)