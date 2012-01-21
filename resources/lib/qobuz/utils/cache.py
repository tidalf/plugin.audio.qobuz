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
import re
import time

import qobuz
from debug import warn, info
from file.write import safe_write

class cache_manager():
    def __init__(self):
        pass
    
    def delete_user_data(self):
        cache = qobuz.path.cache
        if not self._cache_path_exists(cache):
            return False
        list = os.listdir(cache)
        ldel = []
        for f in list:
            if not f.endswith('.dat'): 
                continue
            if f == 'auth.dat':
                ldel.append(f)
            elif f.startswith('userplaylists'):
                ldel.append(f)
            elif f.startswith('playlist'):
                ldel.append(f)
            elif f.startswith('track-url'):
                ldel.append(f)
            elif f == 'purchases.dat':
                ldel.append(f)
        self._delete_files(cache, ldel)
    
    def delete_token_data(self):
        cache = qobuz.path.cache
        if not self._cache_path_exists(cache):
            return False
        list = os.listdir(cache)
        ldel = []
        for f in list:
            if not f.endswith('.dat'): 
                continue
            if f == 'auth.dat':
                ldel.append(f)
            elif f.startswith('track-url'):
                ldel.append(f)
        self._delete_files(cache, ldel)          
            
    def _cache_path_exists(self, path):
        if not path:
            warn(self, "Cache directory is not set")
            return False
        if not os.path.exists(path):
            warn(self, "Cache directory doesn't seem to exist")
            return False
        return True
        
    def _delete_files(self, base_path, list):
        sw = safe_write()
        for f in list:
            info(self, "Deleting file: " + f)
            path = os.path.join(base_path, f)
            sw.unlink(path)
            
    def delete_all_data(self):
        cache = qobuz.path.cache
        if not self._cache_path_exists(cache):
            return False
        list = os.listdir(cache)
        ldel = []
        for f in list:
            if not f.endswith('.dat'):
                continue
            ldel.append(f)
        self._delete_files(cache, ldel)
    