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

    def delete(self, path):
        if not os.path.exists(path):
            return False
        sw = safe_write()
        info(self, "Unlinking " + path)
        return sw.unlink(path)

    def delete_token_data(self):
        cache = qobuz.path.cache
        if not self._cache_path_exists(cache): return False
        ldel = []
        for f in os.listdir(cache):
            if not f.endswith('.dat'): continue
            if not (f.startswith(('auth', 'track-url'))) : continue
            ldel.append(os.path.join(cache, f))
        return self._delete_files(ldel)

    def delete_user_data(self):
        cache = qobuz.path.cache
        if not self._cache_path_exists(cache): return False
        ldel = []
        for f in os.listdir(cache):
            if not f.endswith('.dat'): continue
            ldel.append(os.path.join(cache, f))
        return self._delete_files(ldel)

    def _cache_path_exists(self, path):
        if not path:
            warn(self, "Cache directory is not set")
            return False
        if not os.path.exists(path):
            warn(self, "Cache directory doesn't seem to exist")
            return False
        return True

    def _delete_files(self, list):
        sw = safe_write()
        ret = True
        for file in list:
            if not sw.unlink(file):
                warn(self, "Cannot delete file: " + file)
                ret = False
        return ret

    def delete_all_data(self):
        cache = qobuz.path.cache
        if not self._cache_path_exists(cache):
            return False
        list = []
        self._delete_subdir_data(cache, list)
        sw = safe_write()
        for f in list:
            sw.unlink(f)
            
    def _delete_subdir_data(self, path, files_to_delete = []):
        list = os.listdir(path)
        for file in list:
            newpath = os.path.join(path, file)
            if file.endswith('.dat'):
                files_to_delete.append(newpath)
            elif os.path.isdir(newpath):
                self._delete_subdir_data(newpath, files_to_delete)
        
            