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

import xbmcaddon
import xbmc

from api import QobuzApi
from debug import log, info, warn
import qobuz

"""
 Class QobuzXbmc
"""
class QobuzCore:

    def __init__(self):
        self.data = ""
        self.conn = ""

    def is_logged(self):
        return qobuz.api.auth

    def login(self):
        username = qobuz.addon.getSetting('username')
        password = qobuz.addon.getSetting('password')
        if not username or not password:
            return None
        auth = qobuz.api.login(username, password)
        if not auth: return None
        if auth.get_data()['user']['login'] != username:
            warn(self, "User login mismatch")
            self.delete_user_data()
            auth.delete_cache()
            return None
        return auth

    def delete_user_data(self):
        #try:
            from utils.cache_manager import cache_manager
            c = cache_manager()
            if not c.delete_user_data():
                warn(self, "Fail to erase all specific user data")
                qobuz.gui.notifyH(self, "Cache can be inconsistant")
#        except:
#            warn(self, "Cannot remove user data from cache")
            