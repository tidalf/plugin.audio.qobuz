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
import sys
import os
import hashlib
import pprint

import qobuz
from utils.icacheable import ICacheable
from debug import *
from utils.cache import cache_manager
'''
 Class QobuzAuth

'''
class Cache_authentication(ICacheable):

    def __init__(self, login, password):
        self.login = login
        self.password = password
        super(Cache_authentication, self).__init__(qobuz.path.cache,
                                         'authentication', None, False)
        self.set_cache_refresh(qobuz.addon.getSetting('cache_duration_auth'))
        info(self, "Cache duration: " + str(self.cache_refresh))
        self.fetch_data()

    def hook_pre_refresh(self):
        c = cache_manager()
        c.delete_token_data()

    def _fetch_data(self):
        params = {'x-api-auth-token': 'null',
                  'email': self.login ,
                  'hashed_password': hashlib.md5(self.password).hexdigest() }
        data = qobuz.api._api_request(params, "/api.json/0.1/user/login")
        if not data: return None
        if not 'user' in data: return None
        if not 'id' in data['user']: return None
        if not data['user']['id']: return None
        data['user']['email'] = ''
        data['user']['firstname'] = ''
        data['user']['lastname'] = ''
        return data

