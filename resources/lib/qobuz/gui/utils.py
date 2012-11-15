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
import time

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
class Utils:

    def __init__(self):
        pass

    def notifyH(self, title, text, image = None, mstime = 2000):
        if not image: image = qobuz.image.access.get('qobuzIcon')
        s = 'XBMC.Notification("%s", "%s", "%s", "%s")' % (title, text, mstime, image)
        xbmc.executebuiltin(s)

    def notify(self, title, text, image = None, mstime = 2000):
        if not image: image = qobuz.image.access.get('qobuzIcon')
        l = qobuz.lang
        s = 'XBMC.Notification("%s", "%s", "%s", "%s")' % (l(title), l(text), mstime, image)
        xbmc.executebuiltin(s)

    def show_login_failure(self):
        __language__ = qobuz.lang
        dialog = xbmcgui.Dialog()
        if dialog.yesno(__language__(30008), __language__(30034), __language__(30040)):
            qobuz.addon.openSettings()
            xbmcplugin.endOfDirectory(handle = int(sys.argv[1]), succeeded = False, updateListing = True, cacheToDisc = False)
            return qobuz.boot.dispatch()
        else:
            xbmc.executebuiltin('ActivateWindow(home)')
            return False

    def is_free_account(self):
        data = qobuz.boot.auth.get_data()
        if not data: return True
        # fixme check user rights
        #if not data['user']['credential']['allowed_audio_format_ids']:
        #    return True
        return False

    def popup_free_account(self):
        if qobuz.addon.getSetting('warn_free_account') != 'true':
            return
        dialog = xbmcgui.Dialog()
        ok = dialog.yesno(qobuz.lang(41000), qobuz.lang(41001), qobuz.lang(41002), qobuz.lang(41003))
        if ok:
            qobuz.addon.setSetting('warn_free_account', 'false')

    def executeJSONRPC(self, json):
        return xbmc.executeJSONRPC(json)
