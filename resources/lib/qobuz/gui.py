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
import urllib

import xbmcplugin
import xbmcgui
import xbmc

from constants import *
from debug import *
from debug import __debugging__

import qobuz

'''
    CLASS QobuzGUI
'''
class QobuzGUI:

    def __init__(self):
        pass

    def notifyH(self, title, text, image = None):
        if not image: image = qobuz.image.access.get('qobuzIcon')
        s = 'XBMC.Notification("%s", "%s", "%s", "%s")' % (title, text, 2000, image)
        xbmc.executebuiltin(s)

    def notify(self, title, text, image = None):
        if not image: image = qobuz.image.access.get('qobuzIcon')
        l = qobuz.lang
        s = 'XBMC.Notification("%s", "%s", "%s", "%s")' % (l(title), l(text), 2000, image)
        xbmc.executebuiltin(s)

    def show_login_failure(self):
        __language__ = qobuz.lang
        dialog = xbmcgui.Dialog()
        if dialog.yesno(__language__(30008), __language__(30034), __language__(30040)):
            qobuz.addon.openSettings()
            xbmcplugin.endOfDirectory(handle = int(sys.argv[1]), succeeded = False, updateListing = True, cacheToDisc = False)
            return self.boot.dispatch()
        else:
            xbmc.executebuiltin('ActivateWindow(home)')
            return False
